"""Tests unitaires pour la classe TransactionProcessor"""

import sys
import os
import pandas as pd
import unittest 


#On ajoute le dossier parent du fichier dans les path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.transaction_processor import TransactionProcessor

#creation des DataFrame pour les tests
def make_clean_df() -> pd.DataFrame:
    """DataFrame propre (celui de DataCleaner) pour les tests des methodes de la class transaction_processor"""
    
    Data = {
        "InvoiceNo" :  ["536365", "536366", "536367", "536368", "536369"],
        "StockCode"	:  ["85123A", "71053",  "84406B", "84029G", "84029E"],
        "Description": ["WHITE HANGING HEART T-LIGHT HOLDER",
                        "WHITE METAL LANTERN",
                        "CREAM CUPID HEARTS COAT HANGER",
                        "KNITTED UNION FLAG HOT WATER BOTTLE",
                        "RED WOOLLY HOTTIE WHITE HEART"],
        "Quantity":    [6, 6, 8, 6, 6],
        "InvoiceDate": pd.to_datetime([
            "2010-12-01 08:26",
            "2010-12-01 08:26",
            "2011-01-15 11:00",
            "2011-03-20 14:00",
            "2011-03-20 14:00",
        ]),
        "UnitPrice":  [2.55, 3.39, 2.75, 3.39, 3.39],
        "CustomerID": [17850, 17850, 13047, 12583, 12583],
        "Country":    ["United Kingdom", "France", "France",
                        "United Kingdom", "United Kingdom"],
    }
    return pd.DataFrame(Data)

def make_old_df() -> pd.DataFrame:
    """creation du DataFrame à comme à l'initial (avant le DataCleaner)""" 
    clean = make_clean_df()
    cancelled = pd.DataFrame({
        "InvoiceNo":  ["C536370", "C536371"],
        "StockCode":  ["00A","00B"],
        "Description":["Cancelled A", "Cancelled B"],
        "Quantity":   [-2,5],
        "InvoiceDate":pd.to_datetime([
            "2011-01-01 09:00"] * 2),
        "UnitPrice":  [1.5, 3.0],
        "CustomerID": [17850, 13047],
        "Country":    ["United Kingdom", "France"],
    })
    
    return pd.concat([clean,cancelled], ignore_index=True)
    
def make_supplier_df()-> pd.DataFrame:
    """DataFrame fournisseur pour les tests."""
    return pd.DataFrame({
        "InvoiceNo":   ["536365", "536366", "536367", "536368", "536369"],
        "Fournisseur": ["F100",   "F200",   "F200",   "F300",   "F100"],
    })


def make_continent_df() -> pd.DataFrame:
    """Mapping pays-continent minimal pour les tests."""
    return pd.DataFrame({
        "Country":   ["United Kingdom", "France"],
        "Continent": ["Europe",         "Europe"],
    })
    
def make_processor() -> TransactionProcessor:
    """Création d'une istance de TransactionProcessor prête pour les tests"""
    return TransactionProcessor(
        df = make_clean_df(),
        df_old = make_old_df(),
        supplier_df = make_supplier_df(),
        continent_df = make_continent_df(),
        )


#test pour la methode calculate_total_amount
class TestCalculateTotalAmount(unittest.TestCase):
    """Tests pour calculate_total_amount()"""
    
    #On test si la colonne TotalAmount a bien été créee 
    def test_column_created(self):
        p = make_processor()
        p.calculate_total_amount()
        #excepted = p.df["Quantity"]*p.df["UnitPrice"]
        
        self.assertIn("TotalAmount", p.df.columns,
                    "La colonne TotalAmount doit exister après le calcul.")

    #test pour la methode group_by_country
class TestGroupByCountry(unittest.TestCase):
    """Tests pour group_by_country()."""

    def test_returns_dataframe(self):
        """Vérifie que la méthode retourne un DataFrame."""
        p = make_processor()
        p.calculate_total_amount()
        result = p.group_by_country()
        self.assertIsInstance(result, pd.DataFrame)


if __name__=="__main__":
    unittest.main(verbosity=2)