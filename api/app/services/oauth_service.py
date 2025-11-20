import requests
from typing import Optional
from app.models.oauth_model import OAuthCredentials

class OAuthService:
    def __init__(self, credentials: OAuthCredentials):
        self.credentials = credentials
        self._access_token: Optional[str] = None

    def get_access_token(self, force_refresh: bool = False) -> str:
        """Get or refresh access token"""
        if self._access_token and not force_refresh:
            return self._access_token

        token_payload = {
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
            "refresh_token": self.credentials.refresh_token,
            "grant_type": "refresh_token"
        }

        try:
            response = requests.post(
                self.credentials.token_uri,
                data=token_payload,
                timeout=20
            )
            response.raise_for_status()
            self._access_token = response.json()["access_token"]
            return self._access_token
        except requests.RequestException as e:
            raise ValueError(f"Failed to obtain access token: {str(e)}")