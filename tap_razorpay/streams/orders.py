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

    def get_url(self, next_page_token=None):
        skip_value = next_page_token or 0  
        url = f"{self.api_path}?skip={skip_value}?count=100"
        return url

    def get_next_page_token(self, response):
      
        if 'items' in response and len(response['items']) > 0:
           
            return response['skip'] + 1  
        return None

    def get_stream_data(self, result):
        """
        Extract and transform the relevant records from the paginated response.
        """
        return [
            self.transform_record(record)
            for record in result['items']
        ]
