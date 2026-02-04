import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from utils import Utils

class GoogleApis():
    """Google API Client discovery wrapper.
    
    Provides methods to authenticate and build Google API services.
    """
    @staticmethod
    def authenticate_and_build_google_service(
        service_name: str,
        scopes: list,
        version: str,
        credentials_file: str = 'credentials.json',
        token_file: str = 'token.json',
    ) -> Resource:
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
        creds: Credentials = None
        try:
            # Check stored credentials
            if os.path.exists(token_file) and not os.path.getsize(token_file) == 0 and Utils.is_valid_json(token_file):
                creds = Credentials.from_authorized_user_file(token_file, scopes)
            
            # Check if credentials are valid and refresh if necessary    
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file, 
                        scopes
                    )
                    creds = flow.run_local_server(port=0)
                    Utils.write_json_file(json_str=creds.to_json(), filename=token_file)
            service: Resource = build(service_name, version, credentials=creds)
        except HttpError as error:
            raise TypeError(f"HTTP error during service building: {error}")
        except Exception as error:
            raise Exception(f"{error.__class__}: {error}") from None
        return service