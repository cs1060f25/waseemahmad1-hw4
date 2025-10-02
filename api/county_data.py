# api/county_data.py
# Created with assistance from Generative AI (ChatGPT). I reviewed and tested the code.

import re
import sqlite3
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# Resolve project root; this file lives in api/, DB is one level up at project root.
DB_PATH = (Path(__file__).resolve().parent.parent / "data.db").as_posix()

VALID_MEASURES = {
    "Violent crime rate",
    "Unemployment",
    "Children in poverty",
    "Diabetic screening",
    "Mammography screening",
    "Preventable hospital stays",
    "Uninsured",
    "Sexually transmitted infections",
    "Physical inactivity",
    "Adult obesity",
    "Premature Death",
    "Daily fine particulate matter",
}

ZIP_RE = re.compile(r"^\d{5}$")

def query_rows(zip_code: str, measure_name: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        # Join by county_code to avoid name mismatches (e.g., "Municipio", "County").
        cur.execute(
            """
            SELECT c.*
            FROM zip_county z
            JOIN county_health_rankings c
              ON z.county_code = c.county_code
            WHERE z.zip = ? AND c.measure_name = ?
            """,
            (zip_code, measure_name),
        )
        return cur.fetchall()
    finally:
        conn.close()

@app.post("/county_data")
async def county_data(request: Request):
    """
    POST /county_data
    Body (JSON): {"zip": "02138", "measure_name": "Adult obesity", ...}
    Special case: {"coffee":"teapot"} -> HTTP 418
    Errors:
      - 400 if zip/measure_name missing or malformed
      - 404 if measure invalid or no rows match
    """
    data = await request.json()

    # Teapot takes precedence over all other behavior
    if data.get("coffee") == "teapot":
        raise HTTPException(status_code=418, detail="I'm a teapot")

    # Required fields
    zip_code = data.get("zip")
    measure_name = data.get("measure_name")

    if zip_code is None or measure_name is None:
        raise HTTPException(status_code=400, detail="Missing zip or measure_name")

    # Validate zip as 5 digits (keeps leading zeros)
    if not isinstance(zip_code, str) or not ZIP_RE.fullmatch(zip_code):
        raise HTTPException(status_code=400, detail="zip must be a 5-digit string")

    # Validate measure against whitelist
    if measure_name not in VALID_MEASURES:
        # Spec says invalid zip/measure pair should yield 404
        raise HTTPException(status_code=404, detail="Measure not found")

    rows = query_rows(zip_code, measure_name)
    if not rows:
        raise HTTPException(status_code=404, detail="No data for this zip/measure")

    # Return exactly the county_health_rankings schema (we select c.*)
    return JSONResponse([dict(r) for r in rows])
