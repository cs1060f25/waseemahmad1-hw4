import sqlite3
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()
DB_PATH = "data.db"

@app.post("/county_data")
async def county_data(request: Request):
    data = await request.json()

    if data.get("coffee") == "teapot":
        raise HTTPException(status_code=418, detail="I'm a teapot")

    if "zip" not in data or "measure_name" not in data:
        raise HTTPException(status_code=400, detail="Missing zip or measure_name")

    zip_code = data["zip"]
    measure_name = data["measure_name"]

    valid_measures = {
        "Violent crime rate","Unemployment","Children in poverty","Diabetic screening",
        "Mammography screening","Preventable hospital stays","Uninsured",
        "Sexually transmitted infections","Physical inactivity","Adult obesity",
        "Premature Death","Daily fine particulate matter"
    }
    if measure_name not in valid_measures:
        raise HTTPException(status_code=404, detail="Measure not found")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    query = """
        SELECT c.* 
        FROM zip_county z
        JOIN county_health_rankings c
        ON z.county_code = c.county_code
        WHERE z.zip = ? AND c.measure_name = ?
    """
    cur.execute(query, (zip_code, measure_name))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No data for this zip/measure")

    return JSONResponse([dict(row) for row in rows])
