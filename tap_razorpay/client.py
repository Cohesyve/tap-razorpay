import requests
from singer import utils
import backoff
import time
import json
import os

class RazorpayClient:
    BASE_URL = "https://api.razorpay.com/v1"

    def __init__(self, config):
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.refresh_token = config.get('refresh_token')
        self.config_path = os.path.join(os.path.dirname(__file__), '../config.json')
        self.access_token = config.get('access_token')
        self.expires_at = config.get('expires_at')

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
    def _make_request(self, method, endpoint, params=None, data=None):
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self._get_headers()
        response = requests.request(method, url, headers=headers, params=params, json=data)
        response.raise_for_status()
        return response.json()

    def _get_headers(self):
        self._ensure_access_token()
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def _ensure_access_token(self):
        if not self.access_token or time.time() >= self.expires_at:
            self._refresh_access_token()

    def _refresh_access_token(self):
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }
        response = requests.post("https://auth.razorpay.com/token", data=data)
        response.raise_for_status()
        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.refresh_token = token_data["refresh_token"]
        self.expires_at = time.time() + token_data["expires_in"]
        
        # Update the config file with the new refresh token
        self._update_config_file()

    def _update_config_file(self):
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r') as config_file:
                config = json.load(config_file)
            
            config['refresh_token'] = self.refresh_token
            config['access_token'] = self.access_token
            config['expires_at'] = self.expires_at

            with open(self.config_path, 'w') as config_file:
                json.dump(config, config_file, indent=2)
        else:
            print("Config file path not provided or file not found. Unable to update refresh token.")

    def get(self, endpoint, params=None):
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint, data=None):
        return self._make_request("POST", endpoint, data=data)