"""
Dans cette Partie, on va construire une pipeline ETL permetant l'orchestration complète
"""

import logging
import os
import pandas as pd

from src.data_cleaner import DataCleaner
from src.transaction_processor import TransactionProcessor

#configuration du logger
logger = logging.getLogger(__file__)

class ETLPipeline:
    """
    Elle charge les données, déclenche le nettoyage, les transformations, les analyses, puis sauvegarde le résultat en Parquet.
    
    Attributs
    ---------
    retail_path : str
        Chemin vers le fichier Online_Retail.xlsx.
    supplier_path : str
        Chemin vers le fichier Supplier.csv.
    continent_path : str
        Chemin vers le fichier de mapping pays-continent.
    df : pd.DataFrame
        DataFrame courant (mis à jour à chaque étape du pipeline).
    df_old : pd.DataFrame
        DataFrame brut original conservé pour les analyses nécessitant les annulations.
    results : dict
        Dictionnaire stockant les résultats intermédiaires de chaque analyse.
    """
    
    def __init__(self, retail_path: str, supplier_path: str, continent_path: str):
        """
        Initialise le pipeline avec les chemins des fichiers source.

        Parameters
        ----------
        retail_path : str
        supplier_path : str
        continent_path : str
        """
        self.retail_path = retail_path
        self.supplier_path = supplier_path
        self.continent_path = continent_path

        # Initialisation des DataFrames 
        self.df = None
        self.df_old = None
        self.results = {}

        logger.info("ETLPipeline initialisé.")
        logger.info("  Retail    : %s", retail_path)
        logger.info("  Supplier  : %s", supplier_path)
        logger.info("  Continent : %s", continent_path)
        
    # chargement des sources
    def _load_data(self):
        """Charge les trois fichiers source en DataFrame."""
        logger.info(" ÉTAPE 1 : Chargement des données ")

        # Chargement du fichier principal des transactions
        logger.info("Lecture de %s ...", self.retail_path)
        self.df = pd.read_excel(self.retail_path)
        self.df_old = self.df.copy()   # conservation du brut pour les annulations
        logger.info("Online_Retail chargé : %d lignes, %d colonnes.",
                    self.df.shape[0], self.df.shape[1])

        # Chargement du fichier fournisseurs
        logger.info("Lecture de %s ...", self.supplier_path)
        self.supplier_df = pd.read_csv(self.supplier_path)
        logger.info("Supplier chargé : %d lignes.", len(self.supplier_df))

        # Chargement du mapping pays-continent
        logger.info("Lecture de %s ...", self.continent_path)
        self.continent_df = pd.read_csv(self.continent_path)
        logger.info("Mapping pays-continent chargé : %d entrées.", len(self.continent_df))
        
    #Excécution complete de pipeline
    def run_pipeline(self):
        """
        1-Chargement des données
        2-Nettoyage
        3-Calcul TotalAmount
        4-Regroupement par pays
        5-Statistiques mensuelles
        6-Satistique (France + heure pointe)
        7-Agregation fournisseur
        8-Agregation continent
        """
        logger.info("========== DÉMARRAGE DU PIPELINE ETL ==========")
        
        #1-chargement
        self._load_data()
        
        #2-Nettoyage
        logger.info("--- 2 : Nettoyage de données ---")
        cleaner = DataCleaner(self.df)
        cleaner.remove_duplicates()
        cleaner.handle_missing_values()
        cleaner.filter_valid_transactions()
        self.df = cleaner.clean_df()
        logger.info("Nettoyage terminé.")
        
        #----Traitement (c'est l'etape 3 à 8)
        logger.info("Transformation et Analyse")
        processor = TransactionProcessor(df = self.df, df_old = self.df_old, supplier_df = self.supplier_df, continent_df = self.continent_df )
        
        logger.info("--- 3 : Calcul TotalAmount ---")
        processor.calculate_total_amount()
        
        logger.info("--- 4 : Ventes par pays ---")
        self.results["country_sales"] = processor.group_by_country()
        
        logger.info("--- 5 : Statistiques mensuelles ---")
        self.results["monthly_stats"] = processor.aggregate_monthly_data()
        
        logger.info("--- 6 : Analyse France + heure de pointe ---")
        self.results["stat_data"] = processor.calcul_stat_data()
        
        logger.info("--- 7 : Analyse fournisseurs ---")
        self.results["supplier_data"] = processor.aggregate_supplier_data()
        
        logger.info("--- 8 : Analyse continents ---")
        self.results["world_data"] = processor.aggregate_world_data()
        
        # Récupération du DataFrame final 
        self.df = processor.get_processed_df()
        
        logger.info("========== PIPELINE ETL TERMINÉ avec succès ==========")
        logger.info("DataFrame final : %d lignes, %d colonnes.",
                    self.df.shape[0], self.df.shape[1])
        
    
    #Methode pour la sauvegarde en Parquet
    def save_as_parquet(self, path: str):
        """
        Enregistre le DataFrame final sous forme de fichier Parquet.

        Parameters
        ----------
        path : str
            Chemin complet du fichier de sortie
        """
        if self.df is None or self.df.empty:
            logger.error("Aucune donnée à sauvegarder. Exécutez run_pipeline() d'abord.")
            return
        
        self.df["StockCode"] = self.df["StockCode"].astype(str)

        # Création du dossier de sortie si nécessaire
        outputs = os.path.dirname(path)
        if outputs and not os.path.exists(outputs):
            os.makedirs(outputs)
            logger.info("Dossier de sortie créé : %s", outputs)

        # Sauvegarde au format Parquet (compression snappy pour efficacité)
        self.df.to_parquet(path, index=False, engine="pyarrow")
        size_kb = os.path.getsize(path) / 1024
        logger.info("DataFrame sauvegardé en Parquet : %s (%.1f Ko)", path, size_kb)