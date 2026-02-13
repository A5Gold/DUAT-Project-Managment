# MTR DUAT - Manpower Analysis Router
"""Manpower analysis API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from parsers.manpower_parser import ManpowerParser
from analysis.manpower import ManpowerAnalyzer

router = APIRouter()

# Store manpower state
manpower_state = {"records": [], "total_files": 0}


class ManpowerScanRequest(BaseModel):
    folder_path: str


class ManpowerExportRequest(BaseModel):
    folder_path: str


@router.post("/scan")
async def scan_manpower(request: ManpowerScanRequest):
    """Scan all daily report DOCX files for manpower data."""
    folder = Path(request.folder_path)
    if not folder.exists():
        raise HTTPException(status_code=404, detail="Folder path does not exist")

    try:
        parser = ManpowerParser(folder)
        files = parser.get_report_files()
        records = parser.process_all()
        manpower_state["records"] = records
        manpower_state["total_files"] = len(files)

        total_jobs = sum(len(r.get("jobs", [])) for r in records)
        return {
            "total_files": len(files),
            "total_records": len(records),
            "total_jobs": total_jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis")
async def get_analysis():
    """Get full manpower analysis from scanned data."""
    if not manpower_state["records"]:
        raise HTTPException(status_code=404, detail="No manpower data. Run scan first.")

    analyzer = ManpowerAnalyzer(manpower_state["records"])
    kpis = analyzer.summary_kpis()
    job_type_mp = analyzer.job_type_manpower()
    role_freq = analyzer.role_frequency()
    team_dist = analyzer.team_distribution()
    access = analyzer.work_access_analysis()

    return {
        "kpis": kpis,
        "job_type_manpower": {k: _serialize(v) for k, v in job_type_mp.items()},
        "role_frequency": role_freq[:20],
        "team_distribution": team_dist,
        "work_access": {k: _serialize(v) for k, v in access.items()},
    }


@router.post("/export")
async def export_manpower(request: ManpowerExportRequest):
    """Export manpower analysis to Excel."""
    if not manpower_state["records"]:
        raise HTTPException(status_code=404, detail="No manpower data. Run scan first.")

    folder = Path(request.folder_path)
    from datetime import datetime
    filename = f"Manpower_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    export_path = folder / filename

    try:
        analyzer = ManpowerAnalyzer(manpower_state["records"])
        analyzer.export_excel(export_path)
        return {"filename": filename, "path": str(export_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _serialize(obj):
    """Convert defaultdict and other non-serializable types."""
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize(i) for i in obj]
    return obj
