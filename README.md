# Online Retail — Pipeline ETL Python

> Pipeline ETL orienté objet pour le traitement et l'analyse de données transactionnelles
> d'un retailer en ligne UK (Dec 2010 – Dec 2011). Inclut nettoyage, transformations métier,
> analyses multi-axes, visualisations Jupyter et CI/CD Jenkins + Docker.

---

## Aperçu du projet

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

## Dataset

Source : [UCI Machine Learning Repository](https://archive.ics.uci.edu)

---

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

## Installation

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

---

## Pipeline CI/CD Jenkins

La pipeline CI/CD automatise **build, lint, tests et exécution ETL** à chaque push GitHub.

### Architecture

```
GitHub Push
    │  (Webhook)
    ▼
Jenkins (Docker)
    │
    ├──  Stage 1 : Checkout       Clone + affiche le commit
    ├──  Stage 2 : Build Image    docker build (tags latest + build-N)
    ├──  Stage 3 : Lint           flake8 PEP8 (UNSTABLE si échec, ne bloque pas)
    ├──  Stage 4 : Tests          pytest 34 tests + rapport JUnit XML
    ├──   Stage 5 : ETL Pipeline  python main.py + vérification Parquet
    └──  Stage 6 : Archive        Parquet + logs archivés dans Jenkins
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

## Structure du projet

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
