from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
from api.routes import report_routes
from datetime import datetime

app = FastAPI(title="Autonomous Report Generator UI")

# 1. Base directory pointing to the current file's folder (api/)
BASE_DIR = Path(__file__).resolve().parent

# 2. Force the static directory directly into the writable serverless /tmp folder
STATIC_DIR = Path("/tmp/static")
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 3. Safely look inside the api/templates directory relative to BASE_DIR
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.templates = templates  # so templates accessible inside router

# 🔹 ADD THIS FUNCTION
def basename_filter(path: str):
    return os.path.basename(path)

# 🔹 REGISTER FILTER
templates.env.filters["basename"] = basename_filter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# health check have been added
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "service": "research-report-generation",
        "timestamp": datetime.now().isoformat()
    }

# Register Routes
app.include_router(report_routes.router)
