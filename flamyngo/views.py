import json
import re
import os

from pymongo import MongoClient

from monty.serialization import loadfn
from monty.json import jsanitize

from flask import render_template, request, make_response

from flamyngo import app

from bson.objectid import ObjectId

module_path = os.path.dirname(os.path.abspath(__file__))


SETTINGS = loadfn(os.environ["FLAMYNGO"])
CONN = MongoClient(SETTINGS["db"]["host"], SETTINGS["db"]["port"])
DB = CONN[SETTINGS["db"]["database"]]
if "username" in SETTINGS["db"]:
    DB.authenticate(SETTINGS["db"]["username"], SETTINGS["db"]["password"])
COLL = DB[SETTINGS["db"]["collection"]]


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
    if not criteria:
        criteria = json.loads(search_string)
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
    doc = COLL.find_one(criteria)
    return make_response(render_template(
        'doc.html', doc=json.dumps(jsanitize(doc)))
    )


def parse_criteria(val, vtype):
    if vtype == "int":
        return int(val)
    elif vtype == "float":
        return float(val)
    elif vtype == "str":
        return str(val)
    elif vtype == "objectid":
        return ObjectId(val)
    else:
        return json.loads(val)


if __name__ == "__main__":
    app.run(debug=True)
