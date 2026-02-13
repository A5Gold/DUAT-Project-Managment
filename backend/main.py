# MTR PS-OHLR DUAT - FastAPI Backend
"""
FastAPI backend server for the MTR DUAT application.
Provides REST API endpoints for all analysis operations.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Add backend directory to path for routers
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers import config, parse, dashboard, lag, performance, scurve, export, keyword, manpower

# Create FastAPI app
app = FastAPI(
    title="MTR PS-OHLR DUAT API",
    description="REST API for MTR Progress Dashboard & NTH Analysis",
    version="3.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(config.router, prefix="/api/config", tags=["Configuration"])
app.include_router(parse.router, prefix="/api/parse", tags=["Parsing"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(lag.router, prefix="/api/lag", tags=["Lag Analysis"])
app.include_router(performance.router, prefix="/api/performance", tags=["Performance"])
app.include_router(scurve.router, prefix="/api/scurve", tags=["S-Curve"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(keyword.router, prefix="/api/keyword", tags=["Keyword Search"])
app.include_router(manpower.router, prefix="/api/manpower", tags=["Manpower Analysis"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "MTR DUAT API is running"}


@app.get("/api/health")
async def health_check():
    """API health check."""
    return {"status": "healthy", "version": "3.0.0"}


def start_server(host: str = "127.0.0.1", port: int = 8000):
    """Start the FastAPI server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
