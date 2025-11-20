# API Analytics pour Power BI

API REST pour faciliter l'intégration de données provenant de services tiers (GA4, Mailchimp, Vimeo) dans Power BI.

## Services supportés

- Google Analytics 4 (GA4) 
- Mailchimp
- Vimeo
- LinkedIn

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

### 2. Installer les dépendances

> Cette étape n'est nécessaire que lors de la première installation ou lorsque de nouvelles dépendances sont ajoutées.

```sh
pip install -r requirements.txt
```

## Configuration

### Option 1: Variables d'environnement (Pour un compte)

Ajoutez les clés suivantes au fichier `.env` à la racine du projet:

```sh
# OAuth Google (GA4)
OAUTH_CLIENT_ID=votre_client_id
OAUTH_CLIENT_SECRET=votre_client_secret
OAUTH_REFRESH_TOKEN=votre_refresh_token
OAUTH_TOKEN_URI=https://oauth2.googleapis.com/token
```

### Option 2: Header HTTP (Pour plusieurs comptes)

Les credentials *OAuth* peuvent être passés dans le header `X-OAuth-Credentials` (encodé en base64).

**Obtenir les credentials OAuth pour GA4**

1. Aller sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créer un projet
3. Activer l'API "*Google Analytics Data API*"
4. Créer des credentials OAuth 2.0
5. Obtenir le `refresh_token` via *OAuth Playground*

## Utilisation de l'API

### Démarrer le serveur

> Assurez-vous que l'environnement virtuel est activé.

```sh
uvicorn app.main:app --reload
```
L'API sera disponible à `http://localhost:8000`

### Documentation interactive

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints disponibles

### GET `/ga4`

Récupère des données de Google Analytics 4.

#### Paramètres de requête

- `property_id` (**obligatoire**):  ID de la propriété GA4
- `start_date` : Date de début (YYYY-MM-DD)
- `end_date`: Date de fin (YYYY-MM-DD)
- `metrics` : Liste de métriques
- `dimensions` : Liste de dimensions
- `limit` : Nombre max de résultats

#### Headers

- `X-OAuth-Credentials` : Credentials OAuth encodés en base64
