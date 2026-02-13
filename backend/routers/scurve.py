# MTR DUAT - S-Curve Router
"""S-Curve generation API endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from analysis.scurve import (
    SCurveGenerator,
    calculate_scurve_data,
    plot_scurve,
    generate_scurve_excel
)

router = APIRouter()

# Global generator instance
scurve_gen = SCurveGenerator()


class SCurveRequest(BaseModel):
    project_code: str
    target_qty: float
    start_year: int
    start_week: int
    end_year: int
    end_week: int


@router.post("/set-data")
async def set_data_from_dashboard():
    """Set S-Curve generator data from dashboard."""
    from .dashboard import analyzer as dashboard_analyzer
    
    if dashboard_analyzer.df is None:
        raise HTTPException(status_code=404, detail="No dashboard data available")
    
    scurve_gen.set_data(dashboard_analyzer.df)
    
    return {"success": True, "message": "Data loaded from dashboard"}


@router.post("/calculate")
async def calculate_scurve(request: SCurveRequest):
    """Calculate S-Curve data for a project."""
    if scurve_gen.df is None:
        raise HTTPException(status_code=400, detail="No data loaded")
    
    week_labels, cum_target, cum_actual, progress = calculate_scurve_data(
        scurve_gen.df,
        request.project_code,
        request.target_qty,
        request.start_year,
        request.start_week,
        request.end_year,
        request.end_week
    )
    
    if not week_labels:
        raise HTTPException(
            status_code=404, 
            detail=f"No data found for project {request.project_code}"
        )
    
    return {
        "success": True,
        "project_code": request.project_code,
        "target_qty": request.target_qty,
        "progress_pct": progress,
        "data": {
            "labels": week_labels,
            "cumulative_target": cum_target,
            "cumulative_actual": cum_actual
        }
    }


@router.post("/chart")
async def get_scurve_chart(request: SCurveRequest):
    """Generate S-Curve chart as base64 image."""
    if scurve_gen.df is None:
        raise HTTPException(status_code=400, detail="No data loaded")
    
    week_labels, cum_target, cum_actual, progress = calculate_scurve_data(
        scurve_gen.df,
        request.project_code,
        request.target_qty,
        request.start_year,
        request.start_week,
        request.end_year,
        request.end_week
    )
    
    if not week_labels:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for project {request.project_code}"
        )
    
    img_base64 = plot_scurve(
        week_labels,
        cum_target,
        cum_actual,
        request.project_code,
        request.target_qty
    )
    
    return {
        "image": img_base64,
        "format": "png",
        "progress_pct": progress
    }


@router.post("/excel")
async def generate_scurve_excel_file(request: SCurveRequest):
    """Generate S-Curve Excel report and return download URL."""
    if scurve_gen.df is None:
        raise HTTPException(status_code=400, detail="No data loaded")
    
    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        output_path = Path(tmp.name)
    
    success, progress = generate_scurve_excel(
        scurve_gen.df,
        request.project_code,
        request.target_qty,
        request.start_year,
        request.start_week,
        request.end_year,
        request.end_week,
        output_path
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to generate Excel file")
    
    return FileResponse(
        path=output_path,
        filename=f"SCurve_{request.project_code}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
