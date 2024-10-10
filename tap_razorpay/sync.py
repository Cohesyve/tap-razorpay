import singer
from singer import Transformer, metadata
from .streams import STREAMS
from .client import RazorpayClient

LOGGER = singer.get_logger()

def sync(config, state, catalog):
    client = RazorpayClient(config)

    # Get selected streams
    selected_streams = catalog.get_selected_streams(state)
    
    if not selected_streams:
        LOGGER.warning("No streams were selected")
        return state

    with Transformer() as transformer:
        for stream in selected_streams:
            tap_stream_id = stream.tap_stream_id
            stream_obj = STREAMS[tap_stream_id](client)
            stream_schema = stream.schema.to_dict()
            stream_metadata = metadata.to_map(stream.metadata)

            LOGGER.info('Syncing stream: %s', tap_stream_id)

            state = stream_obj.sync(state, stream_schema, stream_metadata, config, transformer)
            singer.write_state(state)

    return state