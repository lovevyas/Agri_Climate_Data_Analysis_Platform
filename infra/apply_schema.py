

import os
import psycopg2

DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "agri_climate")
DB_USER = os.environ.get("DB_USER", "dbadmin")
DB_PASSWORD = os.environ["DB_PASSWORD"]

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "..", "sql", "schema", "create_tables.sql")

with open(SCHEMA_FILE, "r") as f:
    schema_sql = f.read()

print(f"Connecting to {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}...")
conn = psycopg2.connect(
    host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
)
conn.autocommit = True

with conn.cursor() as cur:
    cur.execute(schema_sql)

print("Schema applied successfully. Tables created:")
with conn.cursor() as cur:
    cur.execute()
    for schema, table in cur.fetchall():
        print(f"  {schema}.{table}")

conn.close()
