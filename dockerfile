FROM python:3.12-slim

LABEL maintainer="Lamine"
LABEL projet="online-retail-etl"
LABEL description="Pipeline ETL Online Retail — image CI/CD"

# Désactive le buffer Python (logs visibles en temps réel dans Jenkins)
ENV PYTHONUNBUFFERED=1
# Désactive la création de fichiers .pyc (allège l'image)
ENV PYTHONDONTWRITEBYTECODE=1
# Répertoire de travail dans le conteneur
ENV APP_HOME=/app

WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir flake8 pytest

COPY . .

RUN mkdir -p output logs

CMD ["python", "main.py"]