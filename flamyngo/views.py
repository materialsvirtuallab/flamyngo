import json
import re
import os

from pymongo import MongoClient

from monty.serialization import loadfn
from monty.json import jsanitize

from flask import render_template, request, make_response, Response

from flamyngo import app

from functools import wraps
from flask import request, Response

module_path = os.path.dirname(os.path.abspath(__file__))


SETTINGS = loadfn(os.environ["FLAMYNGO"])
CONN = MongoClient(SETTINGS["db"]["host"], SETTINGS["db"]["port"])
DB = CONN[SETTINGS["db"]["database"]]
if "username" in SETTINGS["db"]:
    DB.authenticate(SETTINGS["db"]["username"], SETTINGS["db"]["password"])
CNAMES = [d["name"] for d in SETTINGS["collections"]]
CSETTINGS = {d["name"]: d for d in SETTINGS["collections"]}
AUTH_USER = SETTINGS.get("AUTH_USER", None)
AUTH_PASSWD = SETTINGS.get("AUTH_PASSWD", None)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    if AUTH_USER is None:
        return True
    return username == AUTH_USER and password == AUTH_PASSWD


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if (AUTH_USER is not None) and (not auth or not check_auth(
                auth.username, auth.password)):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/', methods=['GET'])
@requires_auth
def index():
    return make_response(render_template('index.html', collections=CNAMES))


@app.route('/query', methods=['GET'])
@requires_auth
def query():
    cname = request.args.get("collection")
    search_string = request.args.get("search_string")
    settings = CSETTINGS[cname]

    criteria = {}
    for regex in settings["query"]:
        if re.match(r'%s' % regex[1], search_string):
            criteria[regex[0]] = process(search_string, regex[2])
            break
    if not criteria:
        criteria = json.loads(search_string)
    results = []
    projection = [t[0] for t in settings["summary"]]
    for r in DB[cname].find(criteria, projection=projection):
        processed = {}
        for m in settings["summary"]:
            k, v = m
            toks = k.split(".")
            try:
                val = r[toks[0]]
                for t in toks[1:]:
                    try:
                        val = val[t]
                    except KeyError:
                        # Handle integer indices
                        val = val[int(t)]
                val = process(val, v.strip())
            except Exception as ex:
                print(str(ex))
                # Return the base value if we can descend into the data.
                val = None
            processed[k] = val
        results.append(processed)
    return make_response(render_template(
        'index.html', collection_name=cname,
        results=results, fields=projection,
        unique_key=settings["unique_key"],
        active_collection=cname,
        collections=CNAMES)
    )


@app.route('/<string:collection_name>/doc/<string:uid>')
@requires_auth
def get_doc(collection_name, uid):
    settings = CSETTINGS[collection_name]
    criteria = {
        settings["unique_key"]: process(uid, settings["unique_key_type"])}
    doc = DB[collection_name].find_one(criteria)
    return make_response(render_template(
        'doc.html', doc=json.dumps(jsanitize(doc)),
        collection_name=collection_name, doc_id=uid)
    )


def process(val, vtype):
    toks = vtype.rsplit(".", 1)
    if len(toks) == 1:
        func = globals()["__builtins__"][toks[0]]
    else:
        mod = __import__(toks[0], globals(), locals(), [toks[1]], 0)
        func = getattr(mod, toks[1])
    return func(val)


if __name__ == "__main__":
    app.run(debug=True)
