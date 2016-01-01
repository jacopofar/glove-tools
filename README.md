# glove-tools

These are sparse tools written to work with [Stanford GloVe vectors](https://github.com/stanfordnlp/GloVe)

schema.sql
----------
Postgres schema to create the DB structures used by the following scripts

load_to_postgres.py
-------------------

Load a vector file inside a Postgres database. Requires psycopg2 and works in Python3

