from typing import Optional, Dict, Any

from authlib.integrations.base_client import OAuthError
from authlib.integrations.requests_client import OAuth2Session

from happy.protocols import AuthProviderProtocol


class GoogleOAuthProvider(AuthProviderProtocol):
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scopes: Optional[list] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes or ['openid', 'email', 'profile']
        self.session: Optional[OAuth2Session] = None
        self.access_token: Optional[Dict[str, Any]] = None
        self.user_info: Optional[Dict[str, Any]] = None

    def __repr__(self):
        return f"<GoogleOAuthProvider(client_id={self.client_id}, redirect_uri={self.redirect_uri}, scopes={self.scopes})>"

    def create_session(self) -> None:
        """Create an OAuth2 session."""
        self.session = OAuth2Session(self.client_id, self.client_secret, self.redirect_uri)

    def get_authorization_url(self) -> str:
        """Get the authorization URL to redirect the user to Google."""
        if self.session is None:
            self.create_session()
        authorization_url, _ = self.session.create_authorization_url(
            'https://accounts.google.com/o/oauth2/auth',
            scope=' '.join(self.scopes)
        )
        return authorization_url

    def retrieve_token(self, authorization_response: str) -> Dict[str, Any]:
        """Fetch the access token from the authorization response."""
        try:
            self.access_token = self.session.fetch_token(
                'https://oauth2.googleapis.com/token',
                authorization_response=authorization_response,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            return self.access_token
        except OAuthError as e:
            raise Exception(f"Failed to retrieve token: {str(e)}")

    def fetch_user_info(self) -> Dict[str, Any]:
        """Retrieve user information from Google."""
        if not self.access_token:
            raise Exception("No access token available.")
        user_info_response = self.session.get('https://www.googleapis.com/oauth2/v3/userinfo')
        if user_info_response.ok:
            self.user_info = user_info_response.json()
            return self.user_info
        else:
            raise Exception("Failed to fetch user info.")

    def logout(self) -> None:
        """Logout the user by clearing the session and token."""
        self.access_token = None
        self.user_info = None
        self.session = None


class OAuthHandler:
    def __init__(self, auth_provider: AuthProviderProtocol):
        self.auth_provider = auth_provider

    def get_auth_url(self) -> str:
        return self.auth_provider.get_authorization_url()

    def retrieve_token(self, authorization_response: str) -> Dict[str, Any]:
        return self.auth_provider.retrieve_token(authorization_response)

    def fetch_user_info(self) -> Dict[str, Any]:
        return self.auth_provider.fetch_user_info()
