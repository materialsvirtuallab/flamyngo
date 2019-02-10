import os
from monty.serialization import loadfn
from flask import Flask

SETTINGS = loadfn(os.environ["FLAMYNGO"])
if SETTINGS.get("template_folder"):
    app = Flask(__name__, template_folder=os.path.abspath(
        SETTINGS["template_folder"]))
else:
    app = Flask(__name__)
from . import views
