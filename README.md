# Flamyngo

Flamyngo is a customizable Flask frontend for MongoDB.

At the most basic level, the aim is to delegate most settings to a YAML
configuration file, which then allows the  underlying code to be reused for
any conceivable collection.

# Usage

Clone or download the code. Install it if you wish.

In the root directory, run:

```bash
python scripts/flm --config <path/to/config.yaml>
```

If `--config` is not provided, it defaults to `$HOME/.flamyngo.yaml`.

# Configuration

A sample commented configuration yaml file is given below.

```yaml
# MongoDB settings
db:
  host: mongo.host.com
  port: 27017
  username: user
  password: password
  database: mydb

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
    # For example, you can take in a float and render it as a fixed decimal.
    summary:
      - [_id, str]
      - [first_name, str]
      - [last_name, str]
      - [phone_number, str]

    # The following defines unique identifiers for each doc. This allows each
    # specific doc to be queried and displayed using this key. If this key is
    # present in the default list of projections, a link will be created to each
    # unique document.
    unique_key: _id
    unique_key_type: bson.objectid.ObjectId

# Basic auth can be set up by specifying user and password below. If these are not
# set, then no authentication.
AUTH_USER: Iam
AUTH_PASSWD: Pink
```
