from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from database.db import get_connection, init_database

app = FastAPI(title="TelemetryPulse AI API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TelemetryInput(BaseModel):
    device_id: str = "mobile-01"
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    altitude: Optional[float] = None
    heading: Optional[float] = None
    battery: Optional[float] = None
    recorded_at: Optional[str] = None

@app.on_event("startup")
def startup():
    init_database()

@app.get("/")
def root():
    return {"project":"TelemetryPulse AI","status":"online","tracker":"/tracker","docs":"/docs"}

@app.get("/tracker", include_in_schema=False)
def tracker():
    return FileResponse(ROOT / "web" / "tracker.html")

@app.get("/health")
def health():
    return {"status":"healthy"}

@app.post("/telemetry")
def receive(data: TelemetryInput):
    ts = data.recorded_at or datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    cur = conn.execute(
        '''INSERT INTO telemetry
        (device_id, latitude, longitude, accuracy, speed, altitude, heading, battery, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (data.device_id,data.latitude,data.longitude,data.accuracy,data.speed,data.altitude,data.heading,data.battery,ts),
    )
    conn.commit()
    ident = cur.lastrowid
    conn.close()
    return {"success":True,"telemetry_id":ident,"device_id":data.device_id,"received_at":ts}

@app.get("/telemetry/latest")
def latest():
    conn = get_connection()
    row = conn.execute("SELECT * FROM telemetry ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return {"data":dict(row) if row else None}

@app.get("/telemetry/history")
def history(limit: int = 100):
    limit = min(max(limit,1),5000)
    conn = get_connection()
    rows = conn.execute("SELECT * FROM telemetry ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    conn.close()
    return {"count":len(rows),"data":[dict(r) for r in rows]}
