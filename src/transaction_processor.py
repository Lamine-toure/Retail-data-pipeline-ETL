"""blablabla"""
import logging 
import pandas as pd 

logger = logging.getLogger(__name__)


class TransactionProcessor:
    """
    Cette classe gère la logique métier pour les transactions. 
    
    Attributs : 
    df:DataFrame après nettoyage (depuis DataCleaner)
    df_old: DataFrame initial 
    supplier_df: le DataFrame des fournisseurs
    continent_df: le DataFrame de mapping pays-continent 
    """
    def __init__(self, df: pd.DataFrame, df_old: pd.DataFrame, supplier_df: pd.DataFrame, continent_df: pd.DataFrame):
        self.df = df.copy()
        self.df_old = df_old.copy()
        self.supplier_df =  supplier_df.copy()
        self.continent_df = continent_df.copy()
        
        #conversion de InvoiceDate en Datetime
        self.df["InvoiceDate"] = pd.to_datetime(self.df["InvoiceDate"])
        
        logger.info("TransactionProcessor initialisé avec %d transactions valides", len(self.df))
        
    #Calcul du montant total de chaque transaction
    def calculate_total_amount(self) -> "TransactionProcessor":
        """
        Calcule le montant total de chaque ligne de transaction et le met dans un colonne
        
        return:
        l'instance courante
        """
        logger.info("Calcul la la colonne TotalAmount (Quantity*UnitPrice).")
        
        self.df["TotalAmount"] = self.df["Quantity"] * self.df["UnitPrice"]
        
        logger.info(
            "TotalAmount à pour minimum %d , pour maximun %d, pour moyenne %d et pour somme total %d", 
                self.df["TotalAmount"].min(), self.df["TotalAmount"].max(), self.df["TotalAmount"].mean(), self.df["TotalAmount"].sum()
            )
        return self
    
    
    #La methode pour le regroupement par pays
    def group_by_country(self) -> pd.DataFrame:
        """Regroupe les données par pays et calcule la somme totale des montants de transaction pour chaque pays
        
        return: un DataFrame
        """
        logger.info("Agrégation par pays.")
        
        #verifion si TotalAmount est dans notre df
        if "TotalAmount" not in self.df.columns:
            logger.info("La colonne TotalAmount absent du DataFrame, on le calcule directement ")
            self.calculate_total_amount()
            
        #Agregation par pays
        country_sales = (
            self.df.groupby("Country")["TotalAmount"].sum().reset_index().sort_values("TotalAmount", ascending=False)
        )
        
        logger.warning("Top 5 pays par ventes :\n%s", country_sales.head(5).to_string(index=False))
        return country_sales
    
    # Methode pour Statistiques mensuelle
    def aggregate_monthly_data(self) ->pd.DataFrame:
        """
        Calcule des statistiques mensuelles :
        - Montant total des ventes par mois
        - Nombre de transactions par mois
        
        return: DataFrame avec [YearMonth, TotalAmount, NbTransactions]
        """
        
        if "TotalAmount" not in self.df.columns:
            logger.warning("La colonne TotalAmount absent du DataFrame, on le calcule directement.")
            self.calculate_total_amount()
            
        # Extraction de la période année-mois dans InvoiceDate
        df_monthly = self.df.copy()
        df_monthly["YearMonth"] = df_monthly["InvoiceDate"].dt.to_period("M")

        #Agregation: montant totale + nombre d'id distinct par moi
        
        monthly_stats = (
            df_monthly.groupby("YearMonth")
            .agg(
                TotalAmount=("TotalAmount", "sum"),
                NbTransactions = ('InvoiceNo', "nunique")
            )
            .reset_index()
            .sort_values("YearMonth")
        )
        logger.info("Statistiques mensuelles calculées sur %d mois.", len(monthly_stats))
        logger.info("\n%s", monthly_stats.to_string(index=False))
        return monthly_stats
    
    #Methode calcul_stat_data pour une analyse detaillé
    def calcul_stat_data(self) ->dict:
        """
        -Produit (StockCode) ayant rapporté le plus de gain en France 
        -Tranche horaire avec le plus grand volume de transaction.

        Returns:
            dict {
            'top_product_france': pd.DataFrame,
            'peak_hour': pd.DataFrame
            }
        """
        logger.info("== Analyse Sattistique : Top produit France + heure de pointe==")
        if "TotalAmount" not in self.df.columns:
            logger.warning("La colonne TotalAmount absent du DataFrame, on le calcule directement")
            self.calculate_total_amount()
        

        # -Produit le plus rentable en France
        logger.info("Filtrage des transactions France.")
        
        df_france = self.df[self.df["Country"]=="France"]
        
        top_france = (
            df_france.groupby("Description")["TotalAmount"]
            .sum()
            .reset_index()
            .sort_values("TotalAmount", ascending=False)
            .reset_index(drop=True)
        )
        
        top_produit = top_france.iloc[0]
        logger.info(
            "Produit top en France : '%s' avec %.2f £ de gains.",
            top_produit["Description"], top_produit["TotalAmount"]
        )
        
        # -Heure de pointe des transactions
        logger.info("Analyse de l'heure de pointe des transactions.")

        df_hours = self.df.copy()

        # Extraction de l'heure depuis InvoiceDate
        df_hours["Hour"] = df_hours["InvoiceDate"].dt.hour

        # Nombre de transactions (invoices distincts) par tranche horaire
        peak_hour_df = (
            df_hours.groupby("Hour")["InvoiceNo"]
            .nunique()  #compte le nbre de facture unique
            .reset_index()
            .rename(columns={"InvoiceNo": "NbTransactions"})
            .sort_values("NbTransactions", ascending=False)
        )

        peak = peak_hour_df.iloc[0]
        logger.info(
            "Heure de pointe : %dh00 avec %d transactions.",
            int(peak["Hour"]), int(peak["NbTransactions"])
        )

        return {
            "top_product_france": top_france,
            "peak_hour": peak_hour_df
        }
    
    #Methode pour l'agrégation par fournisseur
    def aggregate_supplier_data(self) -> dict:
        """
        -Classement des fournisseur par total de vente
        -Classement des fournisseur par total de vente pourl'année 2011 à UK

        Returns:
            dict {
                'global_ranking': DataFrame,
                'UK_2011_ranking': DataFrame,
            }
        """
        logger.info("===Agrégationn des données fournisseur ===")
        
        if "TotalAmount" not in self.df.columns:
            logger.warning("La colonne TotalAmount absent du DataFrame, on le calcule directement.")
            self.calculate_total_amount()
            
        #Jointure entre les transaction et les fournisseur
        logger.info("Jouinture transaction <--> fournisseur")
        
        #mettre les variables au bon forma
        df_left = self.df.copy()
        df_left["InvoiceNo"] = df_left["InvoiceNo"].astype(str)
        df_right = self.supplier_df.copy()
        df_right["InvoiceNo"] = df_right["InvoiceNo"].astype(str)
        
        df_with_supplier = df_left.merge(df_right, on ="InvoiceNo", how="inner")
        logger.info(
            "Après jointure : %d lignes (sur %d transaction valides).", len(df_with_supplier), len(self.df)
        )
        
        #classement des fournisseurs tout pays confondu
        global_ranking = (
            df_with_supplier.groupby("Fournisseur")["TotalAmount"]
            .sum()
            .reset_index()
            .sort_values("TotalAmount", ascending=False)
            .rename(columns={"TotalAmount": "TotalVentes"})
        )
        logger.info("Top 5 fournisseurs (global) :\n%s",
                    global_ranking.head(5).to_string(index=False))
        
        #classement des fournisseurs en UK pour l'année 2011
        logger.info("Filtrage année 2011 et pays UK.")
        df_uk_2011 = df_with_supplier[
            (df_with_supplier["InvoiceDate"].dt.year == 2011) &
            (df_with_supplier["Country"] == "United Kingdom")
        ]
        
        uk_2011_ranking = (
            df_uk_2011.groupby("Fournisseur")["TotalAmount"]
            .sum()
            .reset_index()
            .sort_values("TotalAmount", ascending=False)
            .rename(columns={"TotalAmount": "TotalVentes_UK_2011"})
        )
        logger.info("Top 5 fournisseurs (UK 2011) :\n%s",
                    uk_2011_ranking.head(5).to_string(index=False))
        
        return {
            "global_ranking": global_ranking,
            "uk_2011_ranking": uk_2011_ranking
        }
        
    #Aggregation par Continent
    def aggregate_world_data(self) -> dict:
        """
        -Classement des continant selons les depences
        -Continent avec le plus d'opération annulées.

        Returns:
            dict {
            'continent_spending': pd.DataFrame,
            'most_cancelled_continent': str
            }
        """
        logger.info("== Agrégation des données par continents ==")
        
        if "TotalAmount" not in self.df.columns:
            logger.warning("La colonne TotalAmount absent du DataFrame, on le calcule directement.")
            self.calculate_total_amount()
            
        # -Classement des continant selons les depépences
        df_continents = self.df.merge(self.continent_df, on="Country", how="left")
        
        # Vérification des pays non mappés
        unmapped = df_continents[df_continents["Continent"].isnull()]["Country"].unique()
        if len(unmapped) > 0:
            logger.warning("Pays non mappés vers un continent : %s", list(unmapped))
            
        #regroupement par continent la somme des montant 
        continent_spending = (
            df_continents.groupby("Continent")["TotalAmount"]
            .sum()
            .reset_index()
            .sort_values("TotalAmount", ascending=False)
        )
        logger.info("Classement des continents par dépenses :\n%s",
                    continent_spending.to_string(index=False))
        
        
        # -Continent avec le plus d'opération annulées.
        # On utilise df_old qui contient toutes les transactions (y compris annulées)
        logger.info("Analyse des annulations par continent.")
        
        # Identification des transactions annulées dans le dataset brut
        df_cancelled = self.df_old[
            self.df_old["InvoiceNo"].astype(str).str.startswith("C")
        ].copy()

        # Jointure avec le mapping continent
        df_cancelled = df_cancelled.merge(self.continent_df, on="Country", how="left")

        # Comptage des annulations par continent
        cancelled_by_continent = (
            df_cancelled.groupby("Continent")["InvoiceNo"]
            .count()
            .reset_index()
            .rename(columns={"InvoiceNo": "NbAnnulations"})
            .sort_values("NbAnnulations", ascending=False)
        )
        
        most_cancelled = cancelled_by_continent.iloc[0]["Continent"]
        logger.info("Continent avec le plus d'annulations : %s (%d annulations)",
                    most_cancelled,
                    int(cancelled_by_continent.iloc[0]["NbAnnulations"]))
        logger.info("Détail :\n%s", cancelled_by_continent.to_string(index=False))

        return {
            "continent_spending": continent_spending,
            "cancelled_by_continent": cancelled_by_continent,
            "most_cancelled_continent": most_cancelled
        }


    # retourne le DataFrame enrichi
    def get_processed_df(self) -> pd.DataFrame:
        """Retourne le DataFrame après toutes les transformations."""
        df = self.df.copy()
        df["StockCode"] = df["StockCode"].astype(str)
        return self.df

