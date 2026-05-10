import pickle
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from lib.log import logger

log = logger.get_logger()


TOKEN_PATH = "conf/key/token.pickle"
CREDENTIALS_PATH = "conf/key/credentials.json"
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar',
]

def get_credentials():
    creds = None

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        log.info("Google API credentials are invalid or not found, initiating authentication flow...")

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                log.info("Google API credentials refreshed successfully.")
            except Exception as e:
                log.warning(f"Token refresh failed: {e} — re-running auth flow")
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES
                )
                creds = flow.run_local_server(
                    port=0,
                    access_type="offline",
                    prompt="consent"
                )
        
        else:
            log.info("No valid credentials available, starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(
                port=0,
                access_type="offline",
                prompt="consent"
            )

        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)
        log.info("Google API credentials saved to token.pickle")

    return creds

if __name__ == "__main__":
    creds = get_credentials()
    print(f"Token valid: {creds.valid}")
    print(f"Token expired: {creds.expired}")