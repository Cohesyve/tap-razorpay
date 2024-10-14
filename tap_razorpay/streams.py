import singer
from singer import metadata
from singer.bookmarks import get_bookmark
import json
from pathlib import Path
import pkg_resources

LOGGER = singer.get_logger()

class Stream:
    tap_stream_id = None
    key_properties = ['id']
    replication_method = 'INCREMENTAL'
    valid_replication_keys = ['created_at']
    replication_key = 'created_at'

    def __init__(self, client):
        self.client = client

    @classmethod
    def get_schema(cls):
        schema_path = pkg_resources.resource_filename('tap_razorpay', f"schemas/{cls.tap_stream_id}.json")
        with open(schema_path, "r") as f:
            return json.load(f)

    def get_bookmark(self, state, stream_name):
        return get_bookmark(state, stream_name, self.replication_key)

    def update_bookmark(self, state, stream_name, value):
        singer.write_bookmark(state, stream_name, self.replication_key, value)

    def transform_item(self, item, stream_schema):
        transformed_item = {}
        for key, schema_property in stream_schema['properties'].items():
            value = item.get(key)
            expected_types = schema_property.get('type', ['null'])
            if not isinstance(expected_types, list):
                expected_types = [expected_types]

            if value is None and 'null' in expected_types:
                transformed_item[key] = None
            elif value is not None:
                if 'string' in expected_types:
                    transformed_item[key] = str(value)
                elif 'integer' in expected_types:
                    try:
                        transformed_item[key] = int(value)
                    except (ValueError, TypeError):
                        LOGGER.warning(f"Could not convert {key}: {value} to integer. Setting to None.")
                        transformed_item[key] = None
                elif 'number' in expected_types:
                    try:
                        transformed_item[key] = float(value)
                    except (ValueError, TypeError):
                        LOGGER.warning(f"Could not convert {key}: {value} to number. Setting to None.")
                        transformed_item[key] = None
                elif 'boolean' in expected_types:
                    transformed_item[key] = bool(value)
                else:
                    transformed_item[key] = value
            else:
                LOGGER.warning(f"Unexpected null value for {key}. Schema doesn't allow null.")
                transformed_item[key] = None

        return transformed_item

    def sync(self, state, stream_schema, stream_metadata, config, transformer):
        bookmark = self.get_bookmark(state, self.tap_stream_id)
        params = {
            "count": 100,
            "skip": 0,
        }
        if bookmark:
            params[self.replication_key] = bookmark

        while True:
            data = self.client.get(self.tap_stream_id, params=params)
            if 'items' not in data:
                LOGGER.warning(f"No 'items' found in response for {self.tap_stream_id}")
                break

            for item in data['items']:
                try:
                    transformed_item = self.transform_item(item, stream_schema)
                    singer_transformed_item = transformer.transform(transformed_item, stream_schema, stream_metadata)
                    singer.write_record(self.tap_stream_id, singer_transformed_item)

                    # Update bookmark if necessary
                    if self.replication_key and self.replication_key in transformed_item:
                        new_bookmark = transformed_item[self.replication_key]
                        if new_bookmark and (not bookmark or new_bookmark > bookmark):
                            self.update_bookmark(state, self.tap_stream_id, new_bookmark)
                            bookmark = new_bookmark

                except Exception as e:
                    LOGGER.error(f"Error processing item in {self.tap_stream_id}: {str(e)}")
                    LOGGER.error(f"Problematic item: {json.dumps(item, indent=2)}")
                    continue

            if len(data['items']) < params['count']:
                break

            params['skip'] += params['count']

        return state

class OrdersStream(Stream):
    tap_stream_id = 'orders'

class CustomersStream(Stream):
    tap_stream_id = 'customers'

class PaymentsStream(Stream):
    tap_stream_id = 'payments'

class SettlementsStream(Stream):
    tap_stream_id = 'settlements'

class RefundsStream(Stream):
    tap_stream_id = 'refunds'

class DisputesStream(Stream):
    tap_stream_id = 'disputes'

class ItemsStream(Stream):
    tap_stream_id = 'items'

STREAMS = {
    'orders': OrdersStream,
    'customers': CustomersStream,
    'payments': PaymentsStream,
    'settlements': SettlementsStream,
    'refunds': RefundsStream,
    'disputes': DisputesStream,
    'items': ItemsStream,
}