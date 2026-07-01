import os
import time
import base64
import requests

from config import Config

MPESA_ENV = os.getenv("MPESA_ENV", "sandbox")
CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")

TOKEN_URL = (
    "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    if MPESA_ENV == "sandbox"
    else "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
)


class MpesaToken:
    _token = None
    _expiry = 0

    @classmethod
    def get_token(cls):
        # Return cached token if still valid
        if cls._token and time.time() < cls._expiry - 10:
            return cls._token

        if not CONSUMER_KEY or not CONSUMER_SECRET:
            raise RuntimeError("MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET must be set")

        cred = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
        auth = base64.b64encode(cred.encode()).decode()
        r = requests.get(TOKEN_URL, headers={"Authorization": f"Basic {auth}"})
        r.raise_for_status()
        data = r.json()
        cls._token = data["access_token"]
        cls._expiry = time.time() + int(data.get("expires_in", 3600))
        return cls._token
