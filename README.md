# 🛒 Online Retail — Pipeline ETL Python

> Pipeline ETL orienté objet pour le traitement et l'analyse de données transactionnelles
> d'un retailer en ligne UK (Dec 2010 – Dec 2011). Inclut nettoyage, transformations métier,
> analyses multi-axes, visualisations Jupyter et CI/CD Jenkins + Docker.

---

## 📑 Table des matières

- [Aperçu du projet](#-aperçu-du-projet)
- [Dataset](#-dataset)
- [Architecture du code](#-architecture-du-code)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Tests unitaires](#-tests-unitaires)
- [Visualisations Jupyter](#-visualisations-jupyter)
- [Pipeline CI/CD Jenkins](#-pipeline-cicd-jenkins)
- [Structure du projet](#-structure-du-projet)
- [Technologies](#-technologies)

---

## 🔍 Aperçu du projet

Ce projet implémente un **pipeline ETL complet en Python orienté objet** autour du dataset
*Online Retail* de l'UCI Machine Learning Repository.

Le pipeline réalise dans l'ordre :

1. **Extract** — Chargement des données transactionnelles (Excel) et des fournisseurs (CSV)
2. **Transform** — Nettoyage, calculs, agrégations et analyses métier
3. **Load** — Export du DataFrame enrichi au format **Parquet**

Les résultats sont visualisés dans un **notebook Jupyter** avec KPI cards, graphiques
interactifs et tableaux stylisés. Un pipeline **CI/CD Jenkins + Docker** automatise
les tests et l'exécution à chaque push GitHub.

---

## 📦 Dataset

| Fichier | Description | Lignes |
|---------|-------------|--------|
| `Online_Retail.xlsx` | Transactions UK (01/12/2010 → 09/12/2011) | ~541 909 |
| `Supplier.csv` | Mapping InvoiceNo → Fournisseur | ~25 900 |
| `country_continent_mapping.csv` | Mapping Pays → Continent | 38 pays |

Source : [UCI Machine Learning Repository](https://archive.ics.uci.edu)

### Variables principales

| Variable | Type | Description |
|----------|------|-------------|
| `InvoiceNo` | Categorical | Identifiant transaction (préfixe `C` = annulation) |
| `StockCode` | Categorical | Identifiant produit (5 chiffres) |
| `Description` | Categorical | Nom du produit |
| `Quantity` | Integer | Quantité par ligne de transaction |
| `InvoiceDate` | Date | Date et heure de la transaction |
| `UnitPrice` | Continuous | Prix unitaire en £ |
| `CustomerID` | Categorical | Identifiant client |
| `Country` | Categorical | Pays du client |

---

## 🏗️ Architecture du code

Le projet est structuré en **3 classes POO** :

```
DataCleaner
│
├── remove_duplicates()          Supprime les lignes en double
├── handle_missing_values()      Traite les NaN (CustomerID, Description, UnitPrice)
├── filter_valid_transactions()  Exclut les annulations (InvoiceNo commençant par 'C')
└── get_clean_df()               Retourne le DataFrame nettoyé

TransactionProcessor
│
├── calculate_total_amount()     Ajoute TotalAmount = Quantity × UnitPrice
├── group_by_country()           Somme des ventes par pays (trié décroissant)
├── aggregate_monthly_data()     CA mensuel + nombre de transactions
├── calcul_stat_data()           Top produit France + heure de pointe
├── aggregate_supplier_data()    Classement fournisseurs global + UK 2011
├── aggregate_world_data()       Dépenses par continent + continent le plus annulé
└── get_processed_df()           Retourne le DataFrame enrichi

ETLPipeline
│
├── run_pipeline()               Orchestre les 8 étapes Extract → Transform → Load
└── save_as_parquet(path)        Exporte le DataFrame final en Parquet (pyarrow)
```

### Flux du pipeline

```
Online_Retail.xlsx ──┐
Supplier.csv ─────────┤──► DataCleaner ──► TransactionProcessor ──► output/retail_clean.parquet
country_continent.csv ┘         │                    │
                           (nettoyage)          (analyses)
                                                     │
                                              analyse_resultats.ipynb
```

---

## ⚙️ Installation

### Prérequis

- Python 3.12+
- pip

### Cloner le repo

```bash
git clone https://github.com/TON-USERNAME/online-retail-etl.git
cd online-retail-etl
```

### Installer les dépendances

```bash
pip install -r requirements.txt
```

```
pandas==2.2.2
openpyxl==3.1.2
pyarrow==16.0.0
```

### Ajouter les fichiers de données

Place les fichiers sources dans le dossier `data/` :

```
data/
├── Online_Retail.xlsx
├── Supplier.csv
└── country_continent_mapping.csv   ← déjà inclus dans le repo
```

> `Online_Retail.xlsx` et `Supplier.csv` ne sont pas versionnés (fichiers volumineux).
> Télécharge `Online_Retail.xlsx` depuis [archive.ics.uci.edu](https://archive.ics.uci.edu).

---

## 🚀 Utilisation

### Exécuter le pipeline complet

```bash
python main.py
```

Le pipeline affiche les résultats dans la console et génère :

```
output/retail_clean.parquet   ← DataFrame final enrichi
logs/etl_pipeline.log         ← Logs détaillés de l'exécution
```

### Exemple de sortie console

```
============================================================
  RÉSULTATS DU PIPELINE ETL
============================================================

📊 TOP 10 PAYS PAR VENTES :
       Country    TotalAmount
United Kingdom  8,187,806.36
   Netherlands    284,661.54
          EIRE    263,276.82
           ...

🇫🇷 TOP PRODUIT EN FRANCE :
PAPER CRAFT, LITTLE BIRDIE   2 892.50 £

🕐 HEURE DE POINTE :
12h00 — 2 317 transactions

🌍 CONTINENTS PAR DÉPENSES :
    Europe      Asia    Oceania    ...
```

---

## 🧪 Tests unitaires

**34 tests** couvrant toutes les méthodes de `DataCleaner` et `TransactionProcessor`.

```bash
# Lancer tous les tests
python -m pytest tests/ -v

# Lancer par classe
python -m pytest tests/DataCleanerTest.py -v
python -m pytest tests/TransactionProcessorTest.py -v
```

### Couverture des tests

| Classe | Méthode | Tests |
|--------|---------|-------|
| `DataCleaner` | `remove_duplicates` | 3 |
| `DataCleaner` | `handle_missing_values` | 4 |
| `DataCleaner` | `filter_valid_transactions` | 3 |
| `DataCleaner` | `get_clean_df` / chaînage | 2 |
| `TransactionProcessor` | `calculate_total_amount` | 3 |
| `TransactionProcessor` | `group_by_country` | 4 |
| `TransactionProcessor` | `aggregate_monthly_data` | 3 |
| `TransactionProcessor` | `calcul_stat_data` | 5 |
| `TransactionProcessor` | `aggregate_supplier_data` | 3 |
| `TransactionProcessor` | `aggregate_world_data` | 4 |
| **Total** | | **34 ✅** |

---

## 📊 Visualisations Jupyter

Le notebook `analyse_resultats.ipynb` génère des visualisations complètes à partir
des résultats du pipeline.

```bash
jupyter notebook analyse_resultats.ipynb
```

### Contenu du notebook

| Section | Visualisation |
|---------|---------------|
| 📌 KPI Cards | 5 indicateurs clés (CA, transactions, clients, produits, panier moyen) |
| 🌍 Ventes par pays | Barplot horizontal + camembert Top 15 |
| 📅 Évolution mensuelle | Courbe CA + barres transactions (double axe) |
| 🇫🇷 Analyse France | Top 10 produits + histogramme heure de pointe |
| 🏭 Fournisseurs | Classement global + classement UK 2011 |
| 🌐 Continents | Répartition dépenses + annulations par continent |
| 📋 Tableaux | Tableaux HTML stylisés avec formatage £ |

---

## 🔄 Pipeline CI/CD Jenkins

La pipeline CI/CD automatise **build, lint, tests et exécution ETL** à chaque push GitHub.

### Architecture

```
GitHub Push
    │  (Webhook)
    ▼
Jenkins (Docker)
    │
    ├── 📥 Stage 1 : Checkout       Clone + affiche le commit
    ├── 🐳 Stage 2 : Build Image    docker build (tags latest + build-N)
    ├── 🔍 Stage 3 : Lint           flake8 PEP8 (UNSTABLE si échec, ne bloque pas)
    ├── 🧪 Stage 4 : Tests          pytest 34 tests + rapport JUnit XML
    ├── ⚙️  Stage 5 : ETL Pipeline  python main.py + vérification Parquet
    └── 📦 Stage 6 : Archive        Parquet + logs archivés dans Jenkins
```

### Lancer Jenkins en local

```bash
# Démarre Jenkins (première fois ~60s)
docker compose up -d

# Accès : http://localhost:8080
# Mot de passe initial :
docker exec jenkins-etl cat /var/jenkins_home/secrets/initialAdminPassword
```

### Plugins Jenkins requis

| Plugin | Rôle |
|--------|------|
| Docker Pipeline | Exécution dans conteneurs Docker |
| GitHub Integration | Webhooks et déclenchement automatique |
| Pipeline | Support Jenkinsfile déclaratif |

> **Guide complet de configuration** (webhook ngrok, token GitHub, création du job) :
> voir [`setup_jenkins.md`](setup_jenkins.md)

---

## 📁 Structure du projet

```
online-retail-etl/
│
├── 📄 main.py                        Point d'entrée — lance le pipeline ETL
├── 📄 requirements.txt               Dépendances Python
├── 📄 Dockerfile                     Image Python 3.12 slim pour CI/CD
├── 📄 Jenkinsfile                    Pipeline déclarative Jenkins (6 stages)
├── 📄 docker-compose.yml             Jenkins local (Docker)
├── 📄 setup_jenkins.md               Guide de configuration CI/CD
├── 📓 analyse_resultats.ipynb        Notebook de visualisation
│
├── 📂 src/
│   ├── __init__.py
│   ├── data_cleaner.py               Classe DataCleaner
│   ├── transaction_processor.py      Classe TransactionProcessor
│   └── etl_pipeline.py               Classe ETLPipeline
│
├── 📂 tests/
│   ├── __init__.py
│   ├── DataCleanerTest.py            34 tests unitaires (pytest)
│   └── TransactionProcessorTest.py
│
├── 📂 data/
│   ├── Online_Retail.xlsx            Source principale (non versionné)
│   ├── Supplier.csv                  Données fournisseurs (non versionné)
│   └── country_continent_mapping.csv Mapping pays → continent
│
├── 📂 output/                        Fichiers Parquet générés (non versionné)
├── 📂 logs/                          Logs d'exécution (non versionné)
└── 📂 reports/                       Rapports JUnit XML (non versionné)
```

---

## 🛠️ Technologies

| Technologie | Usage |
|-------------|-------|
| **Python 3.12** | Langage principal |
| **pandas 2.2** | Manipulation des DataFrames |
| **pyarrow 16** | Export Parquet |
| **openpyxl** | Lecture des fichiers Excel |
| **pytest** | Tests unitaires (34 tests) |
| **flake8** | Analyse qualité PEP8 |
| **matplotlib / seaborn** | Visualisations Jupyter |
| **Jupyter Notebook** | Rapport interactif des résultats |
| **Docker** | Conteneurisation et CI/CD |
| **Jenkins** | Pipeline CI/CD automatisée |
| **GitHub** | Versioning + déclenchement webhook |
