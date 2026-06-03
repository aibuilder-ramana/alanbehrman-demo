"""
Run from elevia-alanbehrman/:
    uvicorn service.main:app --port 8020 --reload
"""
import os
import sys

# Ensure project root is on path when started from any working directory
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from service.database import engine
from service import models
from service.routes import patients, appointments, forms

# Create all tables on first run
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AlanBehrman — Patient Intake Service",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(patients.router,     prefix="/api/patients",     tags=["patients"])
app.include_router(appointments.router, prefix="/api",               tags=["appointments"])
app.include_router(forms.router,        prefix="/api",               tags=["forms"])

# Serve the frontend
@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(_ROOT, "index.html"))

@app.get("/intake-v2", include_in_schema=False)
def serve_intake_v2():
    return FileResponse(os.path.join(_ROOT, "intake-v2.html"))

# Static asset directories
for _name, _rel in [("assets", "assets"), ("resources", "resources"), ("data", "data")]:
    _path = os.path.join(_ROOT, _rel)
    os.makedirs(_path, exist_ok=True)
    app.mount(f"/{_name}", StaticFiles(directory=_path), name=_name)
