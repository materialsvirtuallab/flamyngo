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
CNAMES = [d["name"] for d in SETTINGS["collections"]]
CSETTINGS = {d["name"]: d for d in SETTINGS["collections"]}

@app.route('/', methods=['GET'])
def index():
    return make_response(render_template('index.html', collections=CNAMES))


@app.route('/query', methods=['POST'])
def query():
    cname = request.form.get("collection")
    search_string = request.form.get("search_string")
    settings = CSETTINGS[cname]
    
    criteria = {}
    for regex in settings["query"]:
        if re.match(r'%s' % regex[1], search_string):
            criteria[regex[0]] = parse_criteria(search_string, regex[2])
            break
    if not criteria:
        criteria = json.loads(search_string)
    results = list(DB[cname].find(criteria, projection=settings["summary"]))
    return make_response(render_template(
        'index.html', collection_name=cname,
        results=results, fields=settings["summary"],
        unique_key=settings["unique_key"],
        collections=CNAMES)
    )


@app.route('/<string:collection_name>/doc/<string:uid>')
def get_doc(collection_name, uid):
    settings = CSETTINGS[collection_name]
    criteria = {
        settings["unique_key"]: parse_criteria(uid, settings["unique_key_type"])}
    doc = DB[collection_name].find_one(criteria)
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
