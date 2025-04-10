#!/usr/bin/env python3

import singer

import tap_framework

from tap_razorpay.client import RazorpayClient
from tap_razorpay.streams import AVAILABLE_STREAMS
import json

LOGGER = singer.get_logger()  # noqa


class RazorpayRunner(tap_framework.Runner):
    pass

@singer.utils.handle_top_exception(LOGGER)
def main():
    args = singer.utils.parse_args(
        required_config_keys=['client_id', 'client_secret', 'refresh_token'])

    client = RazorpayClient(args.config)


    runner = RazorpayRunner(
        args, client, AVAILABLE_STREAMS)

    if args.discover:
        runner.do_discover()
    else:
        runner.do_sync()


if __name__ == '__main__':
    main()
