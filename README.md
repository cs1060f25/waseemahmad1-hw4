# HW4: CSV to SQLite + County Data API

This repository contains my solution for CS1060 Homework 4.

Part 1 is csv_to_sqlite.py, which converts any valid CSV with a header row into a SQLite database.

It accepts two arguments: the database filename and the CSV file, and creates a table named after the CSV. All columns are stored as TEXT for portability, and valid SQL identifiers are expected as headers.

Part 2 is a FastAPI app deployed on Vercel that exposes a /county_data endpoint backed by the generated data.db.

It returns HTTP 400 if required keys are missing, 404 for invalid measures or no results, and 418 if coffee=teapot is included.

The deployed API is available at https://waseemahmad1-hw4.vercel.app/county_data

To verify functionality, run chmod +x tests.sh && ./tests.sh, which performs a suite of curl-based checks for 200, 400, 404, and 418 responses.
