import pickle
import os
from google.auth.transport.requests import Request

TOKEN_PATH = "conf/key/token.pickle"

def get_credentials():
    with open(TOKEN_PATH, "rb") as token:
        creds = pickle.load(token)
    
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)
    
    return creds

if __name__ == "__main__":
    creds = get_credentials()
    print(f"Token valid: {creds.valid}")
    print(f"Token expired: {creds.expired}")