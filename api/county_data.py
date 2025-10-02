# api/county_data.py
# Created with assistance from Generative AI (ChatGPT). I reviewed and tested the code.

import re
import sqlite3
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse

app = FastAPI()

# DB lives at the repo root; this file is in api/
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
        # Join on 5-digit FIPS: zip_county.county_code == county_health_rankings.fipscode
        cur.execute(
            """
            SELECT c.*
            FROM zip_county z
            JOIN county_health_rankings c
              ON z.county_code = c.fipscode
            WHERE z.zip = ? AND c.measure_name = ?
            """,
            (zip_code, measure_name),
        )
        return cur.fetchall()
    finally:
        conn.close()


@app.get("/")
def root():
    """Friendly landing page for browser GETs."""
    return {
        "message": "Use POST /county_data with a JSON body.",
        "headers": {"Content-Type": "application/json"},
        "example_body": {"zip": "02138", "measure_name": "Adult obesity"},
        "allowed_measures": sorted(list(VALID_MEASURES))[:3] + ["…"],
        "teapot_hint": 'Include {"coffee":"teapot"} to get HTTP 418 (spec requirement).',
    }


@app.get("/county_data")
def county_data_get():
    """Make it explicit that this endpoint expects POST."""
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Use POST /county_data with a JSON body (Content-Type: application/json).",
    )


@app.post("/county_data")
async def county_data(request: Request):
    """
    POST /county_data
    Body (JSON): {"zip": "02138", "measure_name": "Adult obesity", ...}

    Special case:
      - coffee=teapot -> HTTP 418
    Errors:
      - 400 if zip/measure_name missing or zip malformed
      - 404 if measure invalid (not in allowed list) or no rows found
    """
    data = await request.json()

    # Teapot supersedes all other behavior
    if data.get("coffee") == "teapot":
        raise HTTPException(status_code=418, detail="I'm a teapot")

    # Validate required keys
    zip_code = data.get("zip")
    measure_name = data.get("measure_name")

    if zip_code is None or measure_name is None:
        raise HTTPException(status_code=400, detail="Missing zip or measure_name")

    # Enforce 5-digit ZIP as string (keeps leading zeros)
    if not isinstance(zip_code, str) or not ZIP_RE.fullmatch(zip_code):
        raise HTTPException(status_code=400, detail="zip must be a 5-digit string")

    # Enforce allowed measures (spec)
    if measure_name not in VALID_MEASURES:
        raise HTTPException(status_code=404, detail="Measure not found")

    rows = query_rows(zip_code, measure_name)
    if not rows:
        raise HTTPException(status_code=404, detail="No data for this zip/measure")

    # Return rows in exactly the county_health_rankings schema (c.*)
    return JSONResponse([dict(r) for r in rows])
