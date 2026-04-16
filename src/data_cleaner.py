import logging 
import pandas as pd 

logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        logger.info(
            "DataCleaner initialisé avec un DataFrame de %d lignes et %d colonnes.",
            self.df.shape[0],
            self.df.shape[1]
        )
        
    #suppression des doublons
    def remove_duplicates(self) -> "DataCleaner":
        nb_before = len(self.df)
        nb_duplicates = self.df.duplicated().sum()
        
        logger.info(
            "Suppression des doublons : %d doublons détectés sur %d lignes.",
            nb_duplicates,
            nb_before
        )

        self.df = self.df.drop_duplicates()
        
        nb_after = len(self.df)
        logger.info("Après nettoyage : %d lignes restantes.", nb_after)
        
        return self
    
    #Gestion des valeurs manquente
    def handle_missing_values(self) -> "DataCleaner":
        """
        Traitement ds valeurs manquantes (CustomerID, Description, Quantity, UnitPrice)
        en supprimeant les lignes sans identifiant client, sans description ... et quant Qte, prix < 0

        Returns:
            DataCleaner: l'instance courant
        """
        #Colonne CustomerID
        nb_before = len(self.df)
        nb_missing_customer = self.df["CustomerID"].isnull().sum()
        logger.info("Valeur manquante Costomer_ID: %d lignes supprimée", nb_missing_customer)
        self.df = self.df.dropna(subset=["CustomerID"])

        
        #Colonne Description
        nb_desc = self.df["Description"].isnull().sum() #nbre de doublon dans la col description
        logger.info("Valeur manquante Description: %d lignes supprimée", nb_desc)
        self.df = self.df.dropna(subset=["Description"])
        
        #Colonne Quantity et UnitPrice
        nb_invalid_price,nb_invalid_qte = (self.df["Quantity"]<= 0).sum() , (self.df["UnitPrice"]< 0).sum()
        logger.info("%d lignes où la Qte<=0 et %d lignes où la le prix<0 ",nb_invalid_qte,nb_invalid_price)
        #on retire les lignes qui conviennent pas
        self.df = self.df[self.df["Quantity"]>0]
        self.df = self.df[self.df["UnitPrice"]>0]
        
        nb_after = len(self.df)
        logger.info(
            "Au final on a %d lignes restante et %d lignes supprimées ",nb_after, nb_before-nb_after 
            )

        return self
        
    # la methode filter
    def filter_valid_transactions(self) -> "DataCleaner":
        nb_before = len(self.df) #le nbre de ligne initiale
        
        transaction_cancelled = self.df["InvoiceNo"].astype(str).str.startswith("C")
        nb_cancelled = transaction_cancelled.sum()
        logger.info("le nombre de transaction annuler est %d", nb_cancelled)
        self.df = self.df[~transaction_cancelled]
        
        nb_after = len(self.df)
        logger.info(
            "Après filtration on a %d lignes ", nb_after
        )

    #retour du dataframe nettoyé
    def clean_df(self) -> "DataCleaner":
        """df après toutes les Opérations"""
        
        logger.info(
            "notre DataFrame à pour dimmension %s ", self.df.shape)
        return self.df