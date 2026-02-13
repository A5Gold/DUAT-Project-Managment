# MTR DUAT - Export Router
"""Excel export API endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.excel_export import (
    export_dataframe_to_excel,
    create_dashboard_excel,
    export_lag_analysis_report
)

router = APIRouter()


class ExportRequest(BaseModel):
    filename: Optional[str] = None


@router.post("/dashboard")
async def export_dashboard(request: ExportRequest):
    """Export dashboard data to Excel file."""
    from .dashboard import analyzer as dashboard_analyzer
    
    if dashboard_analyzer.df is None or dashboard_analyzer.summary is None:
        raise HTTPException(status_code=400, detail="No dashboard data to export")
    
    # Create temp file
    filename = request.filename or "MTR_DUAT_Dashboard.xlsx"
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        output_path = Path(tmp.name)
    
    # Get raw data columns
    raw_df = dashboard_analyzer.df[["Year", "Day", "Date", "Week", "Project", "Qty Delivered"]].copy()
    
    success = create_dashboard_excel(
        raw_df,
        dashboard_analyzer.summary,
        output_path,
        dashboard_analyzer.nth_trend
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to export dashboard")
    
    return FileResponse(
        path=output_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.post("/lag-analysis")
async def export_lag_analysis(request: ExportRequest):
    """Export lag analysis results to Excel file."""
    from .lag import lag_analyzer
    
    if lag_analyzer.results is None:
        raise HTTPException(status_code=400, detail="No lag analysis results to export")
    
    filename = request.filename or "MTR_DUAT_Lag_Analysis.xlsx"
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        output_path = Path(tmp.name)
    
    success = export_lag_analysis_report(lag_analyzer.results, output_path)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to export lag analysis")
    
    return FileResponse(
        path=output_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/download/{file_type}")
async def download_file(file_type: str):
    """
    Generic download endpoint.
    file_type: 'dashboard' or 'lag-analysis'
    """
    if file_type == "dashboard":
        return await export_dashboard(ExportRequest())
    elif file_type == "lag-analysis":
        return await export_lag_analysis(ExportRequest())
    else:
        raise HTTPException(status_code=400, detail=f"Unknown file type: {file_type}")


@router.post("/save-dashboard")
async def save_dashboard_to_folder(folder_path: str = ""):
    """Save dashboard Excel to the source folder (like the Flet app does)."""
    from .dashboard import analyzer as dashboard_analyzer
    
    if dashboard_analyzer.df is None or dashboard_analyzer.summary is None:
        raise HTTPException(status_code=400, detail="No dashboard data to export")
    
    if not folder_path:
        raise HTTPException(status_code=400, detail="No folder path provided")
    
    folder = Path(folder_path)
    if not folder.exists():
        raise HTTPException(status_code=400, detail="Folder does not exist")
    
    output_file = folder / "Progress Dashboard + NTH.xlsx"
    
    raw_df = dashboard_analyzer.df[["Year", "Day", "Date", "Week", "Project", "Qty Delivered"]].copy()
    
    success = create_dashboard_excel(
        raw_df,
        dashboard_analyzer.summary,
        output_file,
        dashboard_analyzer.nth_trend
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save dashboard Excel")
    
    return {"success": True, "filename": output_file.name, "path": str(output_file)}
