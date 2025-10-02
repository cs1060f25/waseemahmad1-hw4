#!/usr/bin/env python3
"""
csv_to_sqlite.py

Converts a CSV file into a SQLite3 database table.
Usage:
    python3 csv_to_sqlite.py data.db input.csv

Notes:
- Expects the first row of the CSV to contain valid SQL column names (no spaces/quotes).
- Creates a new table with the same name as the CSV filename (without extension).
- Appends table to the DB if it already exists.
- Code authored with assistance from Generative AI (ChatGPT).
"""

import sys
import sqlite3
import csv
import os

def csv_to_sqlite(db_name, csv_file):
    # Derive table name from CSV filename (no extension, lowercased)
    table_name = os.path.splitext(os.path.basename(csv_file))[0]

    # Open connection
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)  # first row is header

        # Create table with TEXT columns
        columns = ", ".join([f"{h} TEXT" for h in headers])
        create_stmt = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
        cur.execute(create_stmt)

        # Insert rows
        placeholders = ", ".join(["?"] * len(headers))
        insert_stmt = f"INSERT INTO {table_name} VALUES ({placeholders})"
        cur.executemany(insert_stmt, reader)

    conn.commit()
    conn.close()
    print(f"Loaded {csv_file} into {db_name} (table: {table_name})")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 csv_to_sqlite.py <database_name> <csv_file>")
        sys.exit(1)

    db_name, csv_file = sys.argv[1], sys.argv[2]
    csv_to_sqlite(db_name, csv_file)
