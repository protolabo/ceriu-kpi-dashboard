from pydantic import BaseModel

class OAuthCredentials(BaseModel):
    client_id: str
    client_secret: str
    refresh_token: str
    token_uri: str