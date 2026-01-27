import requests
import time


class VippsAuth:
    """
    Handles authentication with Vipps API.
    Fetches and caches access tokens.
    """

    def __init__(self, client_id: str, client_secret: str, subscription_key: str, base_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.subscription_key = subscription_key
        self.base_url = base_url

        self._token = None
        self._token_expiry = 0

    def _fetch_new_token(self):
        url = f"{self.base_url}/accessToken/get"

        headers = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
        }

        response = requests.post(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        self._token = data["access_token"]
        self._token_expiry = time.time() + data["expires_in"] - 30  # renew 30s early

    def get_token(self) -> str:
        if not self._token or time.time() >= self._token_expiry:
            self._fetch_new_token()
        return self._token

    def get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json",
        }
