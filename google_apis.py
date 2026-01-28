import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def authenticate_and_build_google_service(
    service_name: str,
    scopes: list,
    version: str,
    credentials_file: str = 'credentials.json',
    token_file: str = 'token.json',
) -> object:
    """Provides a function to authenticate and build a Google API service.
    Reference: https://github.com/googleapis/google-api-python-client/blob/main/docs/oauth-installed.md
    
    Args:
        service_name: the name of the Google API service.
        scopes: the list of scopes to request.
        version: the version of the Google API service.
        credentials_file: the path to the credentials file.
        token_file: the path to the token file.
    Returns:
        A Google API service object.
    Raises:
        TypeError: .
        ValueError: .
    """
    creds = None
    try:
        # Comprobar si ya existen credenciales guardadas
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, scopes)
        
        # Si no hay credenciales válidas, pedir al usuario que inicie sesión    
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, 
                    scopes
                )
                creds = flow.run_local_server(port=0)
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        service = build(service_name, version, credentials=creds)
    except Exception as e:
        raise ValueError(f"Error during authentication or service building: {e}")
    return service