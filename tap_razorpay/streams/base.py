import math
import os
import pytz
import singer
import singer.utils
import singer.metrics
import time
import datetime
import json
import argparse
from tap_razorpay.client import RazorpayClient
from tap_razorpay.config import get_config_start_date
from tap_razorpay.state import incorporate, save_state, \
    get_last_record_value_for_table



from tap_framework.streams import BaseStream as base

LOGGER = singer.get_logger()

DEFAULT_BASE_URL = "https://api.razorpay.com/v1"


class BaseStream(base):
    KEY_PROPERTIES = ['id']
    ACCEPT = None
    CONTENT_TYPE = None
    EXTENDED_BODY_PROPERTIES = {}

    def get_params(self):
        return {}

    def get_body(self):
        return {}

    def get_url(self, path):
        api_base_url = self.config.get("api_base_url")
        if api_base_url is None:
            uri = self.config.get("uri")

            if uri is None:
                api_base_url = DEFAULT_BASE_URL

        return '{}{}'.format(api_base_url, path)

    def transform_record(self, record):
        transformed = base.transform_record(self, record)

        return transformed

    def sync_data(self):
        table = self.TABLE
        LOGGER.info('Syncing data for entity {}'.format(table))

        url = self.get_url(self.api_path)
        params = self.get_params()
        body = self.get_body()

        if self.EXTENDED_BODY_PROPERTIES:
            for key, value in self.EXTENDED_BODY_PROPERTIES.items():
                body[key] = value

        headers = ({key: value for key, value in {
            'Accept': self.ACCEPT,
            'Content-Type': self.CONTENT_TYPE,
        }.items() if value}) or None

        client: RazorpayClient = self.client

        result = client.make_request_json(
            url, self.API_METHOD, params=params, body=body, headers=headers)
        data = self.get_stream_data(result)

        with singer.metrics.record_counter(endpoint=table) as counter:
            for obj in data:
                singer.write_records(
                    table,
                    [obj])

                counter.increment()
        return self.state

   

class PaginatedStream(BaseStream):

    def get_paginated_url(self, skip=0, count=100):
        base_url = self.get_url(self.api_path)
        url = f"{base_url}?skip={int(skip)}&count={int(count)}"
        return url

    def sync_data(self):
        table = self.TABLE
        LOGGER.info('Syncing data for entity {}'.format(table))

        body = self.get_body()

        if self.EXTENDED_BODY_PROPERTIES:
            for key, value in self.EXTENDED_BODY_PROPERTIES.items():
                body[key] = value
                
        client: RazorpayClient = self.client

        headers = ({key: value for key, value in {
            'Accept': self.ACCEPT,
            'Content-Type': self.CONTENT_TYPE,
        }.items() if value}) or None

        page_count = 0
        while True:
            url = self.get_paginated_url(skip=page_count)

            LOGGER.info('Syncing from page {}'.format(page_count))
            try:
                result = client.make_request(
                    url, self.API_METHOD, body=body, headers=headers)
                data = self.get_stream_data(result.json())
                with singer.metrics.record_counter(endpoint=table) as counter:
                    for obj in data:
                        singer.write_records(
                            table,
                            [obj])
                        counter.increment()

                if len(data) < 100:
                    break

                page_count += 100
            except Exception as e:
                LOGGER.error('Error syncing data for entity {}: {}'.format(table, e))
                break
        return self.state

