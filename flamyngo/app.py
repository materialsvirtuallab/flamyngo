"""
Main app. Import settings.
"""

import os

from flask import Flask
from monty.serialization import loadfn

SETTINGS = loadfn(os.environ["FLAMYNGO"])
if SETTINGS.get("template_folder"):
    app = Flask(__name__, template_folder=os.path.abspath(SETTINGS["template_folder"]))
else:
    app = Flask(__name__)
from . import views  # pylint: disable=C0413
