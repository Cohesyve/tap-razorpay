from tap_razorpay.streams.base import PaginatedStream

import singer
import json

LOGGER = singer.get_logger()  # noqa


class RefundsStream(PaginatedStream):
    API_METHOD = 'GET'
    TABLE = 'refunds'
    KEY_PROPERTIES = ["id"]

    @property
    def api_path(self):
        return '/refunds'

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result['items']
        ]
