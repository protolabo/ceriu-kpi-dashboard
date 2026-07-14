# KPI Connectors

Librairie Python cherchant à permettre l'agrégation de multi-sources (GA4, Mailchimp, Vimeo), accompagnée d'une API REST prête à l'emploi pour brancher Power BI sur ces sources afin de faire un tableau de bord KPI.

Le projet se compose de deux parties :

- **`kpi_connectors`** la librairie : des connecteurs réutilisables pour récupérer des données de chaque source, utilisables dans n'importe quel script Python.
- **`app`** une application FastAPI minimale qui expose ces connecteurs via une API REST, consommée par Power BI.

## Services supportés

- Google Analytics 4 (GA4)
- Mailchimp
- Vimeo
- LinkedIn *(à venir)*
- Facebook *(à venir*)

## Structure du projet
```
├── src/kpi_connectors/      # la librairie 
│   ├── auth/                # authentification (OAuth)
│   ├── connectors/          # clients vers les sources (ga4, mailchimp, vimeo)
│   └── models/              # schémas de données
│
└── app/                     # application qui consomme la librairie (serveur web avec FAST API)
    ├── main.py
    ├── config/              # settings
    ├── models/              # APIResponse
    └── endpoints/           # routes GA4, Mailchimp, Vimeo             
```

## Installation

### Prérequis

- Python 3.11+
- `pip`
- `pipenv`. Si vous n'avez pas `pipenv`, installez-le avec `pip install pipenv`.

### 1. Activer l'environnement virtuel

```sh
pipenv shell
```

> Pour quitter l'environnement virtuel, utilisez la commande `exit`.

### 2. Installer le projet

Installez la librairie en mode éditable. Les dépendances sont déclarées dans `pyproject.toml` et seront installées automatiquement.

```sh
pip install -e .
```

> Le mode éditable (`-e`) lie l'installation à vos fichiers source : toute modification du code est prise en compte sans réinstaller. Cette étape n'est nécessaire qu'à la première installation ou lorsque de nouvelles dépendances sont ajoutées.

## Configuration

### Option 1: Variables d'environnement (pour un compte)

Ajoutez les clés suivantes au fichier `.env` à la racine du projet:

```sh
# OAuth Google (GA4)
OAUTH_CLIENT_ID=votre_client_id
OAUTH_CLIENT_SECRET=votre_client_secret
OAUTH_REFRESH_TOKEN=votre_refresh_token
OAUTH_TOKEN_URI=https://oauth2.googleapis.com/token

# Mailchimp
MAILCHIMP_API_KEY=votre_cle_api

# Vimeo
VIMEO_ACCESS_TOKEN=votre_token
```

### Option 2: Header HTTP (pour plusieurs comptes)

Les credentials *OAuth* peuvent être passés dans le header `X-OAuth-Credentials` (encodé en base64).

**Obtenir les credentials OAuth pour GA4**

1. Aller sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créer un projet
3. Activer l'API "*Google Analytics Data API*"
4. Créer des credentials OAuth 2.0
5. Obtenir le `refresh_token` via *OAuth Playground*

## Utilisation

### En tant que librairie

Les connecteurs sont importables directement, sans lancer de serveur :

```python
from kpi_connectors.connectors.mailchimp import fetch_mailchimp_audiences

result = fetch_mailchimp_audiences(api_key="votre_cle-us21")
print(result["total_subscribers"])
for audience in result["audiences"]:
    print(audience["name"], audience["member_count"])
```

### En tant qu'API web

#### Démarrer le serveur

> Assurez-vous que l'environnement virtuel est activé.

```sh
uvicorn app.main:app --reload
```

L'API sera disponible à `http://localhost:8000`

#### Documentation interactive

- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Endpoints disponibles

### GET `/api/v1/ga4`

Récupère des données de Google Analytics 4.

#### Paramètres de requête

- `property_id` (**obligatoire**): ID de la propriété GA4
- `start_date` : Date de début (YYYY-MM-DD)
- `end_date`: Date de fin (YYYY-MM-DD)
- `metrics` : Liste de métriques
- `dimensions` : Liste de dimensions
- `limit` : Nombre max de résultats

#### Headers

- `X-OAuth-Credentials` : Credentials OAuth encodés en base64

### GET `/api/v1/mailchimp/audiences`

Récupère les audiences Mailchimp et le nombre total d'abonnés.

### GET `/api/v1/mailchimp/campaigns/summary`

Récupère le résumé des campagnes Mailchimp.

### GET `/api/v1/vimeo/...`

Récupère les statistiques de visionnement Vimeo.