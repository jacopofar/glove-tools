# glove-tools

These are sparse tools written to work with [Stanford GloVe vectors](https://github.com/stanfordnlp/GloVe)

schema.sql
----------
Postgres schema to create the DB structures used by the following scripts

load_to_postgres.py
-------------------

Loads a vector file inside a Postgres database. Requires psycopg2 and works in Python3

search.py
---------
A few functions to retrieve a word vector and search the nearest neighbor for a given one. It includes a function to store vector balls and dramatically speedup further searches, persisting them on the database.
