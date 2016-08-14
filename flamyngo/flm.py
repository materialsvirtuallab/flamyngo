# coding: utf-8
# Copyright (c) Materials Virtual Lab.
# Distributed under the terms of the BSD License.

from __future__ import division, unicode_literals, print_function

"""
#TODO: Replace with proper module doc.
"""

import os
import argparse
import time
import webbrowser


def run_server(args):
    os.environ["FLAMYNGO"] = args.config
    from flamyngo.app import app
    if args.browser:
        from multiprocessing import Process
        p = Process(target=app.run,
                     kwargs={"debug": args.debug, "host": args.host,
                             "port": args.port})
        p.start()
        time.sleep(2)
        webbrowser.open("http://{}:{}".format(args.host, args.port))
        p.join()
    else:
        app.run(debug=args.debug, host=args.host, port=args.port)


def main():

    parser = argparse.ArgumentParser(
        description="""flamyngo is a basic Flask frontend for querying
        MongoDB collections.""",
        epilog="Author: Shyue Ping Ong")

    parser.add_argument(
        "-c", "--config", dest="config", type=str, nargs="?",
        default=os.path.join(os.environ["HOME"], ".flamyngo.yaml"),
        help="YAML file where the config is stored")
    parser.add_argument(
        "-b", "--browser", dest="browser", action="store_true",
        help="Automatically launch in browser.")
    parser.add_argument(
        "-d", "--debug", dest="debug", action="store_true",
        help="Whether to run in debug mode.")
    parser.add_argument(
        "-hh", "--host", dest="host", type=str, nargs="?",
        default='0.0.0.0',
        help="Host in which to run the server. Defaults to 0.0.0.0.")
    parser.add_argument(
        "-p", "--port", dest="port", type=int, nargs="?",
        default=5000,
        help="Port in which to run the server. Defaults to 5000.")

    args = parser.parse_args()

    run_server(args)


if __name__ == "__main__":
    main()