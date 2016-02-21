import json
import random
import string
import StringIO
import re
import os

from pymongo import MongoClient

from monty.serialization import loadfn
from monty.json import jsanitize

from flask import render_template, request, redirect, make_response,\
    session, jsonify, Markup, Response

from flamyngo import app


module_path = os.path.dirname(os.path.abspath(__file__))


SETTINGS = loadfn(os.environ["FLAMYNGO"])
CONN = MongoClient(SETTINGS["db"]["host"], SETTINGS["db"]["port"])
DB = CONN[SETTINGS["db"]["database"]]
DB.authenticate(SETTINGS["db"]["username"], SETTINGS["db"]["password"])
COLL = DB[SETTINGS["db"]["collection"]]


import pprint

pprint.pprint(SETTINGS)
pprint.pprint(COLL.find_one({}).keys())


@app.route('/', methods=['GET'])
def index():
    return make_response(render_template(
        'index.html', collection_name=SETTINGS["db"]["collection"]))


@app.route('/query', methods=['POST'])
def query():
    search_string = request.form.get("search_string")
    criteria = {}
    for regex in SETTINGS["query"]:
        if re.match(r'%s' % regex[1], search_string):
            criteria[regex[0]] = parse_criteria(search_string, regex[2])
            break
    print(criteria)
    results = list(COLL.find(criteria, projection=SETTINGS["summary"]))
    return make_response(render_template(
        'index.html', collection_name=SETTINGS["db"]["collection"],
        results=results, fields=SETTINGS["summary"],
        unique_key=SETTINGS["unique_key"])
    )


@app.route('/doc/<string:uid>')
def get_doc(uid):
    criteria = {
        SETTINGS["unique_key"]: parse_criteria(uid, SETTINGS["unique_key_type"])}
    print(criteria)
    doc = COLL.find_one(criteria)
    pprint.pprint(doc)
    return jsonify(jsanitize(doc))


def parse_criteria(val, vtype):
    if vtype == "int":
        return int(val)
    elif vtype == "float":
        return float(val)
    elif vtype == "str":
        return str(val)
    else:
        return json.loads(val)


if __name__ == "__main__":
    app.run(debug=True)
