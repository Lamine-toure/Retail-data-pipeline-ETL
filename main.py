"""
Lancement du pipeline complet et affiche les résultats clés.
"""

import logging
import os
import sys
#import pandas as pd

#ajout du repertoire courant au pythonPath
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.etl_pipeline import ETLPipeline

#Configuration du logging (affichage + fichier)
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True) #crée un dossier logs s'il n'existe pas

logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s |%(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        #Affichage dans ma console
        logging.StreamHandler(sys.stdout),
        #sauvegarde dans le fichier log
        logging.FileHandler(os.path.join(LOG_DIR, "ETL_pipeline.log"), encoding = "utf-8")
    ]
)
logger = logging.getLogger("main")

#les chemins vers les fichiers sources 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RETAIL_PATH = os.path.join(BASE_DIR, "Data", "Online_Retail.xlsx")
SUPPLIER_PATH = os.path.join(BASE_DIR, "Data", "Supplier.csv")
CONTINENT_PATH = os.path.join(BASE_DIR, "Data", "continent_df.csv")


os.makedirs(os.path.join(BASE_DIR, "outputs"), exist_ok=True)
PARQUET_PATH = os.path.join(BASE_DIR, "outputs", "retail_clean.parquet")

def main():
    """Fonction principale qui orchestre l'exécution de l'ETL"""
    
    logger.info("============= Projet ETL ==============")
    
    #instanciation er exécution du pipeline
    pipeline = ETLPipeline(
        retail_path=RETAIL_PATH,
        supplier_path=SUPPLIER_PATH,
        continent_path=CONTINENT_PATH
    )
    pipeline.run_pipeline()
    
    
    # Affichage des résultats clés
    results = pipeline.results

    print(" ===== RÉSULTATS DU PIPELINE ETL =====")


    # Ventes par pays (Top 10)
    print("\n TOP 10 PAYS PAR VENTES :")
    print(results["country_sales"].head(10).to_string(index=False))
    
    
    # Sauvegarde du DataFrame final en Parquet
    pipeline.save_as_parquet(PARQUET_PATH)
    logger.info("Pipeline terminé. Fichier Parquet : %s", PARQUET_PATH)

    
if __name__ == "__main__":
    main()