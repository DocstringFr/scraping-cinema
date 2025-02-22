# Scrapper Cinéma Web

Application web pour afficher les horaires des cinémas, avec un scraper automatique pour récupérer les données.

## Structure du projet

- `scraper/` : Code pour le scraping des données des cinémas
  - `src/` : Sources du scraper
- `data/` : Stockage des données JSON scrappées

## Installation

1. Créer un environnement virtuel :
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Unix
# ou
.venv\Scripts\activate  # Sur Windows
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
```bash
cp .env-default .env
# Éditer .env avec vos configurations
```

## Utilisation

### Scraper

Le scraper peut être exécuté manuellement :
```bash
python -m scraper.src.main
```