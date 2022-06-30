# coding: utf-8
# Copyright (c) Materials Virtual Lab.
# Distributed under the terms of the BSD License.

"""
Main flask app for Flamyngo
"""

import argparse
import os
import time
import webbrowser


def run_server(args):
    """
    Run server
    """
    os.environ["FLAMYNGO"] = args.config
    from flamyngo.app import app, SETTINGS

    if args.browser:
        from multiprocessing import Process

        p = Process(
            target=app.run,
            kwargs={"debug": args.debug, "host": args.host, "port": args.port},
        )
        p.start()
        time.sleep(2)
        webbrowser.open(f"http://{args.host}:{args.port}")
        p.join()
    else:
        app.run(debug=args.debug, host=args.host, port=args.port)


def main():
    """
    Process args
    """
    parser = argparse.ArgumentParser(
        description="""flamyngo is a basic Flask frontend for querying
        MongoDB collections.""",
        epilog="Author: Shyue Ping Ong",
    )

    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        type=str,
        nargs="?",
        default=os.path.join(os.path.expanduser("~"), ".flamyngo.yaml"),
        help="YAML file where the config is stored",
    )
    parser.add_argument(
        "-b",
        "--browser",
        dest="browser",
        action="store_true",
        help="Automatically launch in browser.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="Whether to run in debug mode.",
    )
    parser.add_argument(
        "-hh",
        "--host",
        dest="host",
        type=str,
        nargs="?",
        default="0.0.0.0",
        help="Host in which to run the server. Defaults to 0.0.0.0.",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        type=int,
        nargs="?",
        default=5000,
        help="Port in which to run the server. Defaults to 5000.",
    )

    args = parser.parse_args()

    run_server(args)


if __name__ == "__main__":
    main()
