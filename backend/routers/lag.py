# MTR DUAT - Lag Analysis Router
"""NTH Lag/Lead analysis API endpoints."""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from analysis.lag_analysis import LagAnalyzer, get_status

router = APIRouter()

# Global analyzer instance
lag_analyzer = LagAnalyzer()


class ProjectConfig(BaseModel):
    target_qty: Optional[float] = None
    productivity: Optional[float] = None
    skip: Optional[bool] = None


class CalculateRequest(BaseModel):
    actual_qty_map: Dict[str, float]


@router.post("/load-master")
async def load_project_master(file: UploadFile = File(...)):
    """Load project master from Excel file."""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be an Excel file")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    
    try:
        # Try to get summary from dashboard if available
        from .dashboard import analyzer as dashboard_analyzer
        summary_df = dashboard_analyzer.summary
        
        success = lag_analyzer.load_project_master(tmp_path, summary_df)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to load project master")
        
        return {
            "success": True,
            "filename": file.filename,
            "projects": lag_analyzer.projects,
            "project_count": len(lag_analyzer.projects),
            "descriptions": lag_analyzer.project_descriptions,
            "target_qty_map": lag_analyzer.target_qty_map,
            "productivity_map": lag_analyzer.productivity_map
        }
    finally:
        tmp_path.unlink(missing_ok=True)


@router.get("/projects")
async def get_projects():
    """Get list of loaded projects."""
    if not lag_analyzer.projects:
        raise HTTPException(status_code=404, detail="No projects loaded")
    
    return {
        "projects": lag_analyzer.projects,
        "descriptions": lag_analyzer.project_descriptions,
        "config": lag_analyzer.config
    }


@router.put("/config/{project_no}")
async def update_project_config(project_no: str, config: ProjectConfig):
    """Update configuration for a specific project."""
    if project_no not in lag_analyzer.config:
        lag_analyzer.config[project_no] = {}
    
    if config.target_qty is not None:
        lag_analyzer.config[project_no]["target_qty"] = config.target_qty
    if config.productivity is not None:
        lag_analyzer.config[project_no]["productivity"] = config.productivity
        lag_analyzer.config[project_no]["source"] = "user_input"
    if config.skip is not None:
        lag_analyzer.config[project_no]["skip"] = config.skip
    
    return {"status": "ok", "project": project_no, "config": lag_analyzer.config[project_no]}


@router.post("/calculate")
async def calculate_lag_lead(request: CalculateRequest):
    """Calculate NTH Lag/Lead for all projects."""
    if lag_analyzer.project_master is None:
        raise HTTPException(status_code=400, detail="No project master loaded")
    
    success = lag_analyzer.calculate(request.actual_qty_map)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to calculate lag/lead")
    
    results = lag_analyzer.results.to_dict(orient="records") if lag_analyzer.results is not None else []
    
    return {
        "success": True,
        "last_calculated": lag_analyzer.last_calculated,
        "results": results
    }


@router.get("/results")
async def get_results():
    """Get lag analysis results."""
    if lag_analyzer.results is None:
        raise HTTPException(status_code=404, detail="No results available")
    
    return {
        "last_calculated": lag_analyzer.last_calculated,
        "results": lag_analyzer.results.to_dict(orient="records")
    }


@router.get("/status-legend")
async def get_status_legend():
    """Get status color legend."""
    return {
        "legend": [
            {"status": "URGENT", "color": "red", "threshold": "<= -10"},
            {"status": "BEHIND", "color": "orange", "threshold": "<= -5"},
            {"status": "SLIGHT LAG", "color": "yellow", "threshold": "< 0"},
            {"status": "ON TRACK", "color": "green", "threshold": "< 5"},
            {"status": "AHEAD", "color": "blue", "threshold": ">= 5"}
        ]
    }
