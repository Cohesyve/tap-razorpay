import singer
from singer import utils
from .sync import sync
from .client import RazorpayClient
from .streams import STREAMS
import json

REQUIRED_CONFIG_KEYS = ["client_id", "client_secret", "refresh_token"]

def discover():
    raw_schemas = {}
    for stream_name, stream_class in STREAMS.items():
        schema = stream_class.get_schema()
        raw_schemas[stream_name] = schema
    
    streams = []
    for stream_name, schema in raw_schemas.items():
        stream = {
            'stream': stream_name,
            'tap_stream_id': stream_name,
            'schema': schema,
            'metadata': [
                {
                    'breadcrumb': [],
                    'metadata': {
                        'selected': True,
                        'table-key-properties': STREAMS[stream_name].key_properties,
                        'valid-replication-keys': STREAMS[stream_name].valid_replication_keys,
                        'replication-method': STREAMS[stream_name].replication_method
                    }
                }
            ],
            'key_properties': STREAMS[stream_name].key_properties,
            'replication_method': STREAMS[stream_name].replication_method,
        }
        streams.append(stream)

    return {'streams': streams}

def main():
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    if args.discover:
        catalog = discover()
        print(json.dumps(catalog, indent=2))
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog = discover()
        
        sync(args.config, args.state, catalog)

if __name__ == "__main__":
    main()