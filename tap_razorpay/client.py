



import requests
from singer import utils
import backoff
import time
import json
import os
import singer
from tap_razorpay.config import update_config

LOGGER = singer.get_logger()


class RazorpayClient:
    BASE_URL = "https://api.razorpay.com/v1"
    MAX_TRIES = 8


    def __init__(self, config):
        
        self.config = config
        self.get_authorization()

    def _ensure_access_token(self):
        if not self.config.get('access_token') or not self.config.get('expires_at') or self.config.get('expires_at') <= time.time():
            return self._refresh_access_token()
        else: 
            return self.config.get('access_token')

    def _refresh_access_token(self):
        data = {
            "client_id": self.config.get("client_id"),
            "client_secret": self.config.get("client_secret"),
            "refresh_token": self.config.get("refresh_token"),
            "grant_type": "refresh_token"
        }
        response = requests.post("https://auth.razorpay.com/token", data=data)
        response.raise_for_status()
        token_data = response.json()
        updated_config=self.config
        updated_config['access_token']=token_data["access_token"]
        updated_config['refresh_token']=token_data["refresh_token"]
        updated_config['expires_at']=time.time()+token_data["expires_in"]
        update_config(updated_config)

        return token_data["access_token"]

    def get_authorization(self):
        return self._ensure_access_token()
       

    def make_request(self, url, method, params=None, body=None, headers=None, attempts=0):
        LOGGER.info("Making {} request to {} ({})".format(method, url, params))
        
        if headers is None:
            headers = {
                'Content-Type': 'application/json',
                'Accept': '*',
                "Authorization": f"Bearer {self.config.get('access_token')}",
            }

        if method == 'GET':
            body = None

        params_exists = params is not None
        body_exists = body is not None

        if params_exists and body_exists:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                json=body
            )
        elif params_exists and not body_exists:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params
            )        
        elif body_exists and not params_exists:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=body
            )
        else:
            response = requests.request(
                method,
                url,
                headers=headers
            )

        message = f"[Status Code: {response.status_code}] Response: {response.text}"
        LOGGER.info(message)
        if str(response.status_code) == "400":
            LOGGER.info(f"URL: {url}")
            LOGGER.info(f"Method: {method}")
            LOGGER.info(f"Params: {params}")
            LOGGER.info(f"Headers: {headers}")
            LOGGER.info(f"Body: {body}")

        if attempts < self.MAX_TRIES and response.status_code not in [200, 201, 202]:
            if response.status_code == 401:
                LOGGER.info(f"[Status Code: {response.status_code}] Attempt {attempts} of {self.MAX_TRIES}: Received unauthorized error code, retrying: {response.text}")
                self.access_token = self.get_authorization()
            elif response.status_code == 425:
                # dont make anymore requests
                LOGGER.info("Duplicate request. Stopping")
                return response
            else:
                sleep_duration = 2 ** attempts
                message = f"[Status Code: {response.status_code}] Attempt {attempts} of {self.MAX_TRIES}: Error: {response.text}, Sleeping: {sleep_duration} seconds"
                LOGGER.warning(message)
                time.sleep(sleep_duration)

            return self.make_request(url, method, params, body, headers, attempts+1)

        if response.status_code not in [200, 201, 202]:
            message = f"[Status Code: {response.status_code}] Error {response.text} for url {response.url}"
            LOGGER.error(message)
            raise RuntimeError(message)

        return response

    def make_request_json(self, url, method, params=None, body=None, headers=None):
        return self.make_request(url, method, params, body, headers).json()
