# SIG Madagascar

Application web de cartographie des ressources naturelles de Madagascar, destinée à explorer les sites miniers, agricoles et énergétiques. L’écran reprend la maquette fournie : navigation à gauche, tableau de bord, panneau de sélection des ressources superposé à la carte, bascule Plan/Satellite et fiche de site. Les limites géographiques officielles et les chiffres affichés dépendent des données chargées dans PostGIS.

## Prérequis

- Docker avec Docker Compose
- Python 3.11 ou plus récent
- Accès Internet pour télécharger les limites depuis geoBoundaries et les tuiles cartographiques

## Installation

Depuis le dossier du projet :

```bash
cp .env.example .env
# Renseigner DB_PASSWORD dans .env
# Ne partagez jamais ce fichier et ne le versionnez pas.
docker compose up -d
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed.py
python scripts/import_regions.py
```

Le schéma `db/schema.sql` est exécuté automatiquement à la première initialisation du volume Postgres. `seed.py` est idempotent. `import_regions.py` télécharge geoBoundaries ADM1; si le téléchargement échoue, téléchargez le GeoJSON ADM1 de Madagascar et lancez `python scripts/import_regions.py chemin/MDG_ADM1.geojson`.

## Lancement

```bash
uvicorn app.main:app --reload
```

Ouvrez <http://127.0.0.1:8000>. La documentation interactive de l’API est disponible à <http://127.0.0.1:8000/docs>.

## API

Toutes les routes renvoient du JSON, sauf les géométries qui suivent le format GeoJSON.

| Route | Description |
|---|---|
| `GET /api/health` | État de l’API et de PostGIS (`{"status":"ok","database":"ok"}`) |
| `GET /api/types` | Types de ressources |
| `GET /api/ressources?type=minier` | Ressources, couleurs et nombre de sites |
| `GET /api/sites?ressources=or,argent` | Sites en `FeatureCollection` GeoJSON |
| `GET /api/sites/{id}` | Site et historique de production/prix |
| `GET /api/regions` | Limites GeoJSON et nombre de sites par région |
| `GET /api/dashboard` | Indicateurs, répartitions et liste des sites |

Exemple de réponse pour `/api/sites?ressources=saphir` :

```json
{"type":"FeatureCollection","features":[{"type":"Feature","id":1,"geometry":{"type":"Point","coordinates":[45.2,-22.7]},"properties":{"nom":"Ilakaka","ressource":"saphir","couleur":"#2f5fc4","region":"Ihorombe","quantite":124,"prix_unitaire":525}}]}
```

Les coordonnées et données de production du jeu de démonstration sont indicatives et ne constituent pas des statistiques officielles.

## Base de données

PostgreSQL + PostGIS : `type_ressource` → `ressource` → `site`; `region` contient les limites des régions et est reliée aux sites; `production` contient les quantités et prix annuels liés aux sites; `route` est prévue pour le futur module routier. Des index spatiaux GiST accélèrent les recherches géographiques.

## Faire évoluer les données et l’interface

- **Ajouter une ressource** : ajouter une ligne `ressource` avec le code d’un type existant, un nom, une couleur hexadécimale et une unité. Le panneau cartographique la récupère depuis l’API.
- **Ajouter un site** : insérer un point WGS84 dans `site`, l’associer à une ressource, puis ajouter une ou plusieurs lignes annuelles dans `production`. `scripts/seed.py` montre les requêtes paramétrées et les coordonnées d’exemple.
- **Ajouter un module** : déclarer le module dans `MODULES` dans `app/static/js/app.js`, ajouter une vue dans `app/static/index.html`, puis connecter l’écran aux routes API nécessaires.

## Tests

```bash
pytest
```

Les tests API utilisent des réponses de base simulées pour fonctionner sans serveur PostGIS.

## Sécurité

Ne versionnez jamais `.env` : il est ignoré par Git. Utilisez `.env.example` comme modèle et changez le mot de passe avant toute mise en ligne. Les requêtes SQL de l’API et du script de données utilisent des paramètres liés.

## Pistes d’évolution

- État des routes et affichage par tronçon
- Suivi des camions et positions en temps réel
- Historique des prix et tonnages avec graphiques
# SIG-Localisation-
