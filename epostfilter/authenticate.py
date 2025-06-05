import epostfilter.config as cfg
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

def authenticate() -> Credentials:
    """
    Authenticates the user and returns their credentials.
    This function checks if a token file exists and uses it to authenticate the user.
    If the token is not valid or does not exist, it initiates an OAuth2 flow to obtain new credentials.
    The new credentials are then saved to a token file for future use.
    Returns:
        Credentials: The authenticated user's credentials.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", cfg.scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", cfg.scopes)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds