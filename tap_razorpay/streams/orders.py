from tap_razorpay.streams.base import PaginatedStream
import singer
import json

LOGGER = singer.get_logger()  # noqa

class OrdersStream(PaginatedStream):
    API_METHOD = 'GET'
    TABLE = 'orders'
    KEY_PROPERTIES = ["id"]

    @property
    def api_path(self):
        return '/orders'

    def get_url(self, skip=0, count=100):
        url = f"{self.api_path}?skip={skip}?count={count}"
        return url

    def get_stream_data(self, result):
        """
        Extract and transform the relevant records from the paginated response.
        """
        return [
            self.transform_record(record)
            for record in result['items']
        ]
