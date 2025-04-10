from tap_razorpay.streams.base import PaginatedStream

import singer
import json

LOGGER = singer.get_logger()  # noqa


class DisputesStream(PaginatedStream):
    API_METHOD = 'GET'
    TABLE = 'disputes'
    KEY_PROPERTIES = ["id"]

    @property
    def api_path(self):
        return '/disputes'

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result['items']
        ]
