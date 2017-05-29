import json
import re
import os

from pymongo import MongoClient

from monty.serialization import loadfn
from monty.json import jsanitize

from flask import render_template, make_response
from flask.json import jsonify

from flamyngo.app import app

from functools import wraps
from flask import request, Response

module_path = os.path.dirname(os.path.abspath(__file__))


SETTINGS = loadfn(os.environ["FLAMYNGO"])
CONN = MongoClient(SETTINGS["db"]["host"], SETTINGS["db"]["port"],
                   connect=False)
DB = CONN[SETTINGS["db"]["database"]]
if "username" in SETTINGS["db"]:
    DB.authenticate(SETTINGS["db"]["username"], SETTINGS["db"]["password"])
HELPTXT = SETTINGS.get("help", "")
CNAMES = [d["name"] for d in SETTINGS["collections"]]
CSETTINGS = {d["name"]: d for d in SETTINGS["collections"]}
AUTH_USER = SETTINGS.get("AUTH_USER", None)
AUTH_PASSWD = SETTINGS.get("AUTH_PASSWD", None)
API_KEY = SETTINGS.get("API_KEY", None)


def check_auth(username, password):
    """
    This function is called to check if a username /
    password combination is valid.
    """
    if AUTH_USER is None:
        return True
    return username == AUTH_USER and password == AUTH_PASSWD


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL. You have to login '
        'with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        api_key = request.headers.get("API_KEY") or request.args.get("API_KEY")
        if (API_KEY is not None) and api_key == API_KEY:
            return f(*args, **kwargs)
        if (AUTH_USER is not None) and (not auth or not check_auth(
                auth.username, auth.password)):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def get_mapped_name(settings, name):
    # The following allows used of mapped names in search criteria.
    name_mappings = {v: k for k, v in settings.get("aliases", {}).items()}
    return name_mappings.get(name, name)


def process_search_string(search_string, settings):
    criteria = {}
    for regex in settings["query"]:
        if re.match(r'%s' % regex[1], search_string):
            criteria[regex[0]] = {'$regex' : str(process(search_string, regex[2]))}
            break
    if not criteria:
        clean_search_string = search_string.strip()
        if clean_search_string[0] != "{" or \
                        clean_search_string[-1] != "}":
            clean_search_string = "{" + clean_search_string + "}"
        criteria = json.loads(clean_search_string)

        criteria = {get_mapped_name(settings, k): v
                    for k, v in criteria.items()}
    return criteria


@app.route('/', methods=['GET'])
@requires_auth
def index():
    return make_response(render_template('index.html', collections=CNAMES,
                                         helptext=HELPTXT))


@app.route('/autocomplete', methods=['GET'])
@requires_auth
def autocomplete():
    terms=[]
    criteria={}

    search_string = request.args.get('term')
    cname = request.args.get("collection")

    collection = DB[cname]
    settings = CSETTINGS[cname]

    # if search looks like a special query, autocomplete values
    for regex in settings["query"]:
        if re.match(r'%s' % regex[1], search_string):
            criteria[regex[0]] = {'$regex' : str(process(search_string, regex[2]))}
            projection = {regex[0]: 1}

            results = collection.find(criteria, projection)
            
            if results:
                terms = [ term[regex[0]] for term in results ]

    # if search looks like a query dict, autocomplete keys
    if not criteria and search_string[0:2] == '{"':
        if search_string.count('"')%2 != 0:
            splitted = search_string.split('"')
            previous = splitted[:-1]
            last = splitted[-1]

            # get list of autocomplete keys from settings
            # generic alternative: use a schema analizer like variety.js
            results = _search_dict(settings["autocomplete_keys"], last)

            if results:
                terms = [ '"'.join(previous + [term]) + '":' for term in results ]

    return jsonify(matching_results=jsanitize(list(set(terms))))


@app.route('/query', methods=['GET'])
@requires_auth
def query():
    cname = request.args.get("collection")
    settings = CSETTINGS[cname]
    search_string = request.args.get("search_string")
    projection = [t[0] for t in settings["summary"]]
    fields = None
    results = None
    mapped_names = None
    error_message = None
    try:
        if search_string.strip() != "":
            criteria = process_search_string(search_string, settings)
            results = []
            for r in DB[cname].find(criteria, projection=projection):
                processed = []
                mapped_names = {}
                fields = []
                for m in settings["summary"]:
                    if len(m) == 2:
                        k, v = m
                    else:
                        raise ValueError("Invalid summary settings!")
                    mapped_k = settings.get("aliases", {}).get(k, k)
                    val = _get_val(k, r, v.strip())
                    val = val if val is not None else ""
                    mapped_names[k] = mapped_k
                    processed.append(val)
                    fields.append(mapped_k)
                results.append(processed)
            if not results:
                error_message = "No results!"
        else:
            error_message = "No results!"
    except Exception as ex:
        error_message = str(ex)

    return make_response(render_template(
        'index.html', collection_name=cname,
        results=results, fields=fields, search_string=search_string,
        mapped_names=mapped_names, unique_key=settings["unique_key"],
        active_collection=cname, collections=CNAMES,
        error_message=error_message)
    )


@app.route('/plot', methods=['GET'])
@requires_auth
def plot():
    cname = request.args.get("collection")
    if not cname:
        return make_response(render_template('plot.html', collections=CNAMES))
    plot_type = request.args.get("plot_type") or "scatter"
    search_string = request.args.get("search_string")
    xaxis = request.args.get("xaxis")
    yaxis = request.args.get("yaxis")
    return make_response(render_template(
        'plot.html', collection=cname,
        search_string=search_string, plot_type=plot_type,
        xaxis=xaxis, yaxis=yaxis,
        active_collection=cname,
        collections=CNAMES,
        plot=True)
    )


@app.route('/data', methods=['GET'])
@requires_auth
def get_data():
    cname = request.args.get("collection")
    settings = CSETTINGS[cname]
    search_string = request.args.get("search_string")
    xaxis = request.args.get("xaxis")
    yaxis = request.args.get("yaxis")

    xaxis = get_mapped_name(settings, xaxis)
    yaxis = get_mapped_name(settings, yaxis)

    projection = [xaxis, yaxis]

    if search_string.strip() != "":
        criteria = process_search_string(search_string, settings)
        data = []
        for r in DB[cname].find(criteria, projection=projection):
            x = _get_val(xaxis, r, None)
            y = _get_val(yaxis, r, None)
            if x and y:
                data.append([x, y])
    else:
        data = []
    return jsonify(jsanitize(data))


@app.route('/<string:collection_name>/unique_ids')
@requires_auth
def get_ids(collection_name):
    settings = CSETTINGS[collection_name]
    doc = DB[collection_name].distinct(settings["unique_key"])
    return jsonify(jsanitize(doc))


@app.route('/<string:collection_name>/doc/<string:uid>')
@requires_auth
def get_doc(collection_name, uid):
    return make_response(render_template(
        'doc.html', collection_name=collection_name, doc_id=uid)
    )


@app.route('/<string:collection_name>/doc/<string:uid>/<string:field>')
@requires_auth
def get_doc_field(collection_name, uid, field):
    settings = CSETTINGS[collection_name]
    criteria = {
        settings["unique_key"]: process(uid, settings["unique_key_type"])}
    doc = DB[collection_name].find_one(criteria, projection=[field])
    return Response(str(doc[field]), mimetype='text/plain')


@app.route('/<string:collection_name>/doc/<string:uid>/json')
@requires_auth
def get_doc_json(collection_name, uid):
    settings = CSETTINGS[collection_name]
    criteria = {
        settings["unique_key"]: process(uid, settings["unique_key_type"])}
    doc = DB[collection_name].find_one(criteria)
    return jsonify(jsanitize(doc))


def process(val, vtype):
    if vtype:
        toks = vtype.rsplit(".", 1)
        if len(toks) == 1:
            func = globals()["__builtins__"][toks[0]]
        else:
            mod = __import__(toks[0], globals(), locals(), [toks[1]], 0)
            func = getattr(mod, toks[1])
        return func(val)
    else:
        try:
            if float(val) == int(val):
                return int(val)
            return float(val)
        except:
            try:
                return float(val)
            except:
                # Y is string.
                return val


def _get_val(k, d, processing_func):
    toks = k.split(".")
    try:
        val = d[toks[0]]
        for t in toks[1:]:
            try:
                val = val[t]
            except KeyError:
                # Handle integer indices
                val = val[int(t)]
        val = process(val, processing_func)
    except Exception as ex:
        # Return the base value if we cannot descend into the data.
        val = None
    return val


def _search_dict(dictionary, substr):
    result = []
    for key in dictionary:
        if substr.lower() in key.lower():
            result.append(key)   
    return result


if __name__ == "__main__":
    app.run(debug=True)
