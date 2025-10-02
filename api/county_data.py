# api/county_data.py
import re
import sqlite3
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

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
        cur.execute(
            """
            SELECT c.*
            FROM zip_county z
            JOIN county_health_rankings c
              ON z.county_code = c.fipscode   -- <<<<<< key fix (5-digit FIPS to 5-digit FIPS)
            WHERE z.zip = ? AND c.measure_name = ?
            """,
            (zip_code, measure_name),
        )
        return cur.fetchall()
    finally:
        conn.close()

@app.post("/county_data")
async def county_data(request: Request):
    data = await request.json()

    if data.get("coffee") == "teapot":
        raise HTTPException(status_code=418, detail="I'm a teapot")

    zip_code = data.get("zip")
    measure_name = data.get("measure_name")

    if zip_code is None or measure_name is None:
        raise HTTPException(status_code=400, detail="Missing zip or measure_name")

    if not isinstance(zip_code, str) or not ZIP_RE.fullmatch(zip_code):
        raise HTTPException(status_code=400, detail="zip must be a 5-digit string")

    if measure_name not in VALID_MEASURES:
        raise HTTPException(status_code=404, detail="Measure not found")

    rows = query_rows(zip_code, measure_name)
    if not rows:
        raise HTTPException(status_code=404, detail="No data for this zip/measure")

    return JSONResponse([dict(r) for r in rows])
