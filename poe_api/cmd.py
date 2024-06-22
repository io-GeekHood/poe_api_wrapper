import argparse
from argparse import ArgumentParser
from poe_api.server import rest_server
from poe_api.config.config_model import Api_Metrics
# read commandline args to initiate server (runtime starts here !)
def main():
    parser = ArgumentParser(
        prog="poe bots api wrapper",
        description="api wrapper for pdf classification",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subcommands = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands',
        help='additional help',
        dest='subcommand',
    )
    run_parser = subcommands.add_parser(
        'run',
        help='Run the rest server',
    )
    run_parser.add_argument(
        '-H', '--host',
        type=str,
        default="0.0.0.0",
        help='host to serve on',
    )
    run_parser.add_argument(
        '-p', '--port',
        type=int,
        default=9000,
        help='Port to listen on',
    )
    run_parser.add_argument(
        '-w', '--num-workers',
        type=int,
        default=1,
        help='Number of workers',
    )
    run_parser.add_argument(
        '-v', '--version',
        type=str,
        default="v1",
        help='Api Version',
    )
    run_parser.add_argument(
        '-a', '--loglevel',
        type=str,
        default="info",
        help='Api logging level',
    )
    args = parser.parse_args()
    if args.subcommand == 'run':
        api_metrics = Api_Metrics(
            host=args.host,
            port=args.port,
            version=args.version,
            num_workers=args.num_workers,
            loglevel=args.loglevel
        )
        rest_server(api_metrics)
    else:
        parser.print_help()
    return None


if __name__ == "__main__":
    main()


