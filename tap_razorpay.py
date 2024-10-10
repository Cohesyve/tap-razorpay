import singer
import requests
import json
from datetime import datetime, timedelta

LOGGER = singer.get_logger()

AUTH_URL = "https://auth.razorpay.com/token"
BASE_URL = "https://api.razorpay.com/v1"
CONFIG = {}
TOKEN = {}

def get_auth_header():
    if 'access_token' not in TOKEN or TOKEN['expires_at'] <= datetime.now():
        refresh_token()
    return {'Authorization': f"Bearer {TOKEN['access_token']}"}

def refresh_token():
    url = AUTH_URL
    data = {
        'client_id': CONFIG['client_id'],
        'client_secret': CONFIG['client_secret'],
        'grant_type': 'refresh_token',
        'refresh_token': CONFIG['refresh_token']
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    token_data = response.json()
    TOKEN.update({
        'access_token': token_data['access_token'],
        'refresh_token': token_data['refresh_token'],
        'expires_at': datetime.now() + timedelta(seconds=token_data['expires_in'])
    })
    # Update the config file with the new refresh token
    CONFIG['refresh_token'] = TOKEN['refresh_token']
    with open('config.json', 'w') as config_file:
        json.dump(CONFIG, config_file, indent=2)

def request(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    headers = get_auth_header()
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def sync_resource(resource_name, schema):
    singer.write_schema(resource_name, schema, ["id"])

    params = {"count": 100, "skip": 0}
    while True:
        data = request(resource_name, params)
        if 'items' not in data:
            break
        for item in data['items']:
            singer.write_record(resource_name, item)
        if len(data['items']) < params['count']:
            break
        params['skip'] += params['count']

def sync_orders():
    schema = {
        "properties": {
            "id": {"type": "string"},
            "amount": {"type": "integer"},
            "currency": {"type": "string"},
            "status": {"type": "string"},
            "created_at": {"type": "integer"},
        },
        "type": "object",
    }
    sync_resource("orders", schema)

def sync_customers():
    schema = {
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "email": {"type": "string"},
            "contact": {"type": "string"},
            "created_at": {"type": "integer"},
        },
        "type": "object",
    }
    sync_resource("customers", schema)

def sync_payments():
    schema = {
        "properties": {
            "id": {"type": "string"},
            "amount": {"type": "integer"},
            "currency": {"type": "string"},
            "status": {"type": "string"},
            "order_id": {"type": "string"},
            "method": {"type": "string"},
            "created_at": {"type": "integer"},
        },
        "type": "object",
    }
    sync_resource("payments", schema)

def sync_settlements():
    schema = {
        "properties": {
            "id": {"type": "string"},
            "amount": {"type": "integer"},
            "status": {"type": "string"},
            "fees": {"type": "integer"},
            "tax": {"type": "integer"},
            "utr": {"type": "string"},
            "created_at": {"type": "integer"},
        },
        "type": "object",
    }
    sync_resource("settlements", schema)

def sync_refunds():
    schema = {
        "properties": {
            "id": {"type": "string"},
            "payment_id": {"type": "string"},
            "amount": {"type": "integer"},
            "status": {"type": "string"},
            "speed_processed": {"type": "string"},
            "created_at": {"type": "integer"},
        },
        "type": "object",
    }
    sync_resource("refunds", schema)

def sync_disputes():
    schema = {
        "properties": {
            "id": {"type": "string"},
            "payment_id": {"type": "string"},
            "amount": {"type": "integer"},
            "currency": {"type": "string"},
            "status": {"type": "string"},
            "reason": {"type": "string"},
            "created_at": {"type": "integer"},
        },
        "type": "object",
    }
    sync_resource("disputes", schema)

def sync_items():
    schema = {
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "description": {"type": "string"},
            "amount": {"type": "integer"},
            "currency": {"type": "string"},
            "active": {"type": "boolean"},
            "created_at": {"type": "integer"},
        },
        "type": "object",
    }
    sync_resource("items", schema)

def main():
    args = singer.utils.parse_args(["client_id", "client_secret", "refresh_token"])
    CONFIG.update(args.config)

    # Initialize the token
    refresh_token()

    sync_orders()
    sync_customers()
    sync_payments()
    sync_settlements()
    sync_refunds()
    sync_disputes()
    sync_items()

if __name__ == "__main__":
    main()