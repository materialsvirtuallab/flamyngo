# Flamyngo

Flamyngo is a customizable Flask frontend for MongoDB.

At the most basic level, the aim is to delegate most settings to a YAML
configuration file, which then allows the  underlying code to be reused for
any conceivable collection. Querying and display is restricted to a single
collection for now. However, the code can serve as a starting point for more
complex setups to support multiple collections.

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

collections:
  -
    name: mycoll

    # These set the special queries as an ordered list of [<key>, <regex string>, <type>].
    # If the query string satisfies any of the regex, the Mongo query is set as
    # {<key>: type(<search_string>)}. This allows for much more friendly setups for common
    # queries that do not require a user to type in verbose Mongo criteria. Each
    # regex should be uniquely identifying.
    # Supported types include int, float, str, objectid.
    # If none of the regex works, the criteria is interpreted as a Mongo-like dict query.
    query:
      - [last_name, '^[A-Za-z]+$', str]
      - [phone_number, '^[0-9]+$', int]

    # A default list of projections to display as a table. Only keys in the root of
    # the document is supported right now.
    summary:
      - _id
      - first_name
      - last_name
      - phone_number

    # The following defines unique identifiers for each doc. This allows each
    # specific doc to be queried and displayed using this key. If this key is
    # present in the default list of projections, a link will be created to each
    # unique document.
    unique_key: _id
    unique_key_type: bson.objectid.ObjectId
```
