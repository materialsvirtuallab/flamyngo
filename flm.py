#!/usr/bin/env python

import os
import argparse

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2012, The Materials Virtual Lab"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyuep@gmail.com"
__date__ = "7/30/14"


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="""flamyngo is a basic Flask frontend for querying
        MongoDB collections.""",
        epilog="Author: Shyue Ping Ong")

    parser.add_argument(
        "-c", "--config", dest="config", type=str, nargs="?",
        default=os.path.join(os.environ["HOME"], ".flamyngo.yaml"),
        help="YAML file where the config is stored")

    args = parser.parse_args()

    port = int(os.environ.get("PORT", 5000))
    os.environ["FLAMYNGO"] = args.config
    from flamyngo import app
    app.run(debug=True, host='0.0.0.0', port=port)

