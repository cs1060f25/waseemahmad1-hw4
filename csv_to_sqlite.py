#!/usr/bin/env python3
"""
csv_to_sqlite.py
Converts a CSV with a header row into a SQLite3 table named after the CSV filename.
Usage:
  python3 csv_to_sqlite.py data.db input.csv

Notes:
- Expects header names to already be valid SQL identifiers (per assignment).
- All columns are stored as TEXT to keep it simple/portable.
- Code authored with assistance from Generative AI (ChatGPT). I reviewed and tested the code.
"""

import sys
import sqlite3
import csv
import os

def csv_to_sqlite(db_name, csv_file):
    table_name = os.path.splitext(os.path.basename(csv_file))[0]

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)

        cols = ", ".join([f"{h} TEXT" for h in headers])
        cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({cols});")

        placeholders = ", ".join(["?"] * len(headers))
        cur.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", reader)

    conn.commit()
    conn.close()
    print(f"Loaded {csv_file} into {db_name} (table: {table_name})")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 csv_to_sqlite.py <database_name> <csv_file>")
        sys.exit(1)

    db_name, csv_file = sys.argv[1], sys.argv[2]
    csv_to_sqlite(db_name, csv_file)
