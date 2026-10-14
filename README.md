# Prédiction des prix immobiliers au Maroc

Projet de Machine Learning comprenant la collecte et la préparation de données immobilières, des notebooks d’analyse et de modélisation, une API Flask et une interface React avec Material UI.

## Fonctionnalités

- Estimation des prix pour les appartements, maisons, villas, terrains, bureaux et locaux commerciaux.
- Sélection de la ville et du quartier.
- Prédiction à partir de la surface, des équipements et des caractéristiques propres au type de bien.

## Organisation

- `app.py` : API Flask (`GET /villes`, `GET /quartiers`, `POST /predict`).
- `mon-app/` : interface React.
- `models/` : modèles exportés avec Joblib.
- `appart/`, `maison/`, `villa/`, `terrain/`, `bureaux/`, `local/` : scripts de collecte, CSV et notebooks.

## Installation et lancement local

Depuis la racine du projet, avec Python et Node.js installés :

```bash
python -m venv .venv
```

Activation sous Windows : `.venv\Scripts\activate` ; sous Linux/macOS : `source .venv/bin/activate`.

```bash
pip install -r requirements.txt
python app.py
```

Dans un second terminal :

```bash
cd mon-app
npm ci
npm start
```

L’interface utilise `http://localhost:5000` pour accéder à l’API. Le serveur Flask est configuré pour le développement local.

## Notebooks

Dans le dossier du type de bien concerné, suivre l’ordre : `scrapping_*.py`, `cleaning_*.ipynb`, `EDA_*.ipynb`, `general_analysis_*.ipynb`, puis `ML_*.ipynb`. Plusieurs étapes utilisent une base MySQL locale `avito_db` : adapter la connexion et créer les tables nécessaires. Les fichiers `conversion.ipynb` servent à importer les CSV dans MySQL.

Les notebooks de modélisation exportent les modèles dans leur dossier courant : copier les exports dans `models/` pour les utiliser avec l’API.

## Données et limites

Les données proviennent d’annonces Avito ; les prix correspondent aux prix affichés, pas nécessairement aux transactions réalisées. Les liens d’annonces ont été retirés des CSV et les sorties des notebooks ont été effacées pour la publication. Les fichiers internes MySQL et les dépendances installées ne sont pas inclus.

Les versions Python des dépendances de l’environnement original ne sont pas documentées. La compatibilité des modèles sérialisés avec les versions installées doit être vérifiée ; un réentraînement peut être nécessaire. Les fichiers Joblib doivent uniquement être chargés depuis une source de confiance.

Le dépôt conserve le travail original de modélisation. Une validation indépendante de la qualité des prédictions, notamment de l’encodage du quartier à partir des prix et de la séparation entraînement/test, reste nécessaire. Aucun score global vérifié n’est annoncé ici.
