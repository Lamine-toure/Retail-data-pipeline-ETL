"""
Test unitaire pour la classe DataClenner 
Execution: python -m pytest tests/DataCleanerTest.py -v   
"""

import sys
import os
import pandas as pd
import unittest 

#print("blabla")

#ajout du dossier parent du fichier courrant dans le chemin de recherche des modules Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


from src.data_cleaner import DataCleaner

def make_sample_df() -> pd.DataFrame:
    """
    Crée un DataFrame de test représentatif avec :
    - doublons
    - valeurs manquantes (CustomerID)
    - transactions annulées (InvoiceNo commençant par 'C')
    - prix invalide (<= 0)
    """
    data = {
    "InvoiceNo":   ["536365", "536365", "536366", "C536367", "536368", "536369"],
    "StockCode":   ["85123A", "85123A", "71053",  "84406B",  "84029G", "84029E"],
    "Description": ["WHITE HANGING HEART", "WHITE HANGING HEART",
                "WHITE METAL LANTERN", None,
                "KNITTED UNION FLAG", "RED WOOLLY HOTTIE"],
    "Quantity":    [6, 6, 6, 8, 6, 6],
    "InvoiceDate": pd.to_datetime(["2010-12-01 08:26"] * 6),
    "UnitPrice":   [2.55, 2.55, 3.39, 2.75, 3.39, -1.0],
    "CustomerID":  [17850, 17850, 17850, None, 17850, 17850],
    "Country":     ["United Kingdom"] * 6,
    }
    return pd.DataFrame(data)

class TestRemoveDuplicates(unittest.TestCase):
    """Tests pour la méthode remove_duplicates()."""

    def test_removes_exact_duplicates(self):
        """Vérifie que les lignes identiques sont bien supprimées."""
        df = make_sample_df()
        print(df)
        cleaner = DataCleaner(df)
        cleaner.remove_duplicates()
        print(cleaner.df)
        # Les lignes 0 et 1 sont identiques 
        self.assertEqual(len(cleaner.df), 5,
                        "Il doit rester 5 lignes après suppression du doublon.")

    
    #def test_no_duplicates_unchanged(self):
    #    """Vérifie qu'un DataFrame sans doublon n'est pas modifié."""
    #    df = make_sample_df().drop_duplicates()
    #    nb_before = len(df)
    #    cleaner = DataCleaner(df)
    #    cleaner.remove_duplicates()
    #    self.assertEqual(len(cleaner.df), nb_before,
    #                    "Sans doublon le nombre de lignes ne doit pas changer.")
    
class TestHandleMissingValues(unittest.TestCase):
    """Tests pour la méthode handle_missing_values()."""
    
    def test_removes_missing_customer_id(self):
        """Vérifie la suppression des lignes avec CustomerID manquant."""
        df = make_sample_df().drop_duplicates()
        cleaner = DataCleaner(df)
        cleaner.handle_missing_values()
        self.assertFalse(cleaner.df["CustomerID"].isnull().any(),
                        "Aucune valeur manquante ne doit rester dans CustomerID.")

class TestFilterValidTransactions(unittest.TestCase):
    """Tests pour la méthode filter_valid_transactions()."""
    
    def test_remove_canceled_transaction(self):
        """Vérifions que les InvoiceNo commençant par C sont bien supprimés"""
        df = make_sample_df().drop_duplicates()
        cleaner = DataCleaner(df)
        cleaner.filter_valid_transactions()
        cancelled = cleaner.df["InvoiceNo"].astype(str).str.startswith("C")
        
        self.assertFalse(cancelled.any(), "Aucune transaction annulée ne doit exister")
        
    

if __name__ == "__main__":
    unittest.main(verbosity=2)