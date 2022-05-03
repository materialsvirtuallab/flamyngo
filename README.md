# Flamyngo

Flamyngo is a YAML-powered Flask frontend for MongoDB. The aim is to delegate 
most settings to a YAML configuration file, which then allows the  underlying 
code to be reused for any conceivable collection. The official web page is at
https://materialsvirtuallab.github.io/flamyngo/.

Complete change log: [link](https://materialsvirtuallab.github.io/flamyngo//CHANGES).

# Usage

Install via pip:

```bash
pip install flamyngo
```

Create your `.flamyngo.yaml`.

```bash
flm --config <path/to/config.yaml>
```

If `--config` is not provided, it defaults to `~/.flamyngo.yaml`.

# Configuration

A sample commented configuration yaml file is given below. You can start from
the one below and customize it to suit your needs.

```yaml
# Provide an optional title for your app.
title: "My Flamyngo App"

# Provide some optional help text (html format) for the query.
help: "Supported queries: last name (string)"

# Uncomment the parameter below to provide an optional template folder, which
# will be passed into the Flamyngo app. Path to the template folder should be
# specified relative to localtion where flm is run. If not provided, the
# default provided in the flamyngo.templates will be used. It is highly
# recommended that you start from the default provided and make only stylistic
# changes. It is imperative you do not change the variable names in the Jinja
# templates or Flamyngo will not work.

# template_folder: my_templates

# MongoDB settings
db:
  host: mongo.host.com
  port: 27017
  username: user
  password: password
  database: mydb
# Alternatively, MongoDB settings can just be provided as a connection string.
# dnspython must be installed if you are using the connection string method.
#  connection_string: "mongodb+srv://user:password@mydb.mongodb.net/"


# List of collection settings. Note that more than one collection is supported,
# though only one collection can be queried at any one time.
collections:
  -
    name: mycoll

    # These set the special queries as an ordered list of [<key>, <regex string>, <type>].
    # If the query string satisfies any of the regex, the Mongo query is set as
    # {<key>: type(<search_string>)}. This allows for much more friendly setups for common
    # queries that do not require a user to type in verbose Mongo criteria. Each
    # regex should be uniquely identifying.
    # Types can be any kind of callable function that takes in a string and return
    # a value without other arguments. E.g., int, str, float, etc. You can support
    # more powerful conversions by writing your own processing function, e.g., 
    # mymodule.convert_degress_to_radians. 
    # If none of the regex works, the criteria is interpreted as a Mongo-like dict query.
    query:
      - [last_name, '^[A-Za-z]+$', str]
      - [phone_number, '^[0-9]+$', int]

    # A default list of projection key, processing function to display as a table. 
    # Again, processing function can be any callable, and you can define your own.
    # You can also supply any Python formatting string (starts with %) as the processing
    # function. For example, "%.1f" would format that quantity as a float with one
    # decimal.
    summary:
      - [_id, str]
      - [first_name, str]
      - [last_name, str]
      - [phone_number, str]
      - [age, "%d"]
        
    # Aliases for various fields. These are used to display short names in the summary
    # table. You can also directly perform queries using the short names instead of
    # using the long names.
    aliases:
      phone_number: number

    # Initial sorting for summary. Use asc for ascending and desc for descending.
    # Note that the aliased name (if any) should be used for sorting.
    sort: [last_name, asc]

    # The following defines unique identifiers for each doc. This allows each
    # specific doc to be queried and displayed using this key. If this key is
    # present in the default list of projections, a link will be created to each
    # unique document.
    unique_key: _id
    unique_key_type: bson.objectid.ObjectId
    
    # The following defines keys to exclude from the doc view.
    # This is sometimes useful (or necessary) to reduce the size of the
    # individual documents being viewed (for very large documents).
    # This only affects the doc view.
    doc_exclude:
      - key_to_exclude

# Basic auth can be set up by specifying user and password below. If these are not
# set, then no authentication. Note that this is not the most secure. It is merely
# used for a basic setup. For high security, look into proper implementations.
AUTH_USER: Iam
AUTH_PASSWD: Pink
API_KEY: IamPink
```

# URLs

Assuming that you are running on local host at port 5000, the initial
landing page will be at http://localhost:5000.

Pages for individual docs following the format 
http://localhost:5000/[collection_name]/doc/[unique_id].

# REST API

* Getting all unique ids for a collection: http://localhost:5000/[collection_name]/unique_ids
* Getting individual docs as a json response: http://localhost:5000/[collection_name]/doc/[unique_id]/json.
* Getting a field of an individual doc as a plain text response: http://localhost:5000/[collection_name]/doc/[unique_id]/<field>.
