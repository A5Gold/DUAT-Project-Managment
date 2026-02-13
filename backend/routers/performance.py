# MTR DUAT - Performance Router
"""Performance analysis API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import sys
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from analysis.performance import (
    PerformanceAnalyzer,
    calculate_performance_metrics,
    get_recovery_path,
    plot_performance_chart,
    plot_cumulative_progress
)

router = APIRouter()

# Import shared analyzer from services
from backend.services import perf_analyzer


class AnalyzeRequest(BaseModel):
    project_code: str
    target_productivity: float = 3.0
    target_qty: Optional[float] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None


class RecoveryRequest(BaseModel):
    target_qty: float
    actual_qty: float
    remaining_weeks: int
    current_productivity: float


@router.post("/set-data")
async def set_data_from_dashboard():
    """Set performance analyzer data from dashboard."""
    from backend.services import dashboard_analyzer
    
    if dashboard_analyzer.df is None:
        raise HTTPException(status_code=404, detail="No dashboard data available")
    
    perf_analyzer.set_data(dashboard_analyzer.df)
    
    return {"success": True, "message": "Data loaded from dashboard"}


@router.get("/projects")
async def get_available_projects():
    """Get list of projects with data."""
    projects = perf_analyzer.get_available_projects()
    
    if not projects:
        raise HTTPException(status_code=404, detail="No projects available")
    
    return {"projects": projects}


@router.post("/analyze")
async def analyze_project(request: AnalyzeRequest):
    """Analyze performance for a specific project."""
    if perf_analyzer.df is None:
        raise HTTPException(status_code=400, detail="No data loaded")
    
    result = perf_analyzer.analyze(
        request.project_code,
        request.target_productivity,
        request.target_qty,
        request.start_year,
        request.end_year
    )
    
    if not result:
        raise HTTPException(status_code=404, detail=f"No data found for project {request.project_code}")
    
    # Convert weekly_data DataFrame to list
    if 'weekly_data' in result:
        result['weekly_data'] = result['weekly_data'].to_dict(orient='records')
    
    return {"success": True, "metrics": result}


@router.get("/breakdown")
async def get_weekly_breakdown():
    """Get weekly breakdown for current project."""
    breakdown = perf_analyzer.get_weekly_breakdown()
    
    if not breakdown:
        raise HTTPException(status_code=404, detail="No breakdown available")
    
    return {"breakdown": breakdown}


@router.post("/recovery")
async def calculate_recovery(request: RecoveryRequest):
    """Calculate recovery path to meet target."""
    result = get_recovery_path(
        request.target_qty,
        request.actual_qty,
        request.remaining_weeks,
        request.current_productivity
    )
    
    return {"recovery": result}


@router.get("/chart/weekly/{project_code}")
async def get_weekly_chart(project_code: str, target_productivity: float = 3.0):
    """Get weekly performance chart as base64 image."""
    if perf_analyzer.df is None:
        raise HTTPException(status_code=400, detail="No data loaded")
    
    metrics = calculate_performance_metrics(perf_analyzer.df, project_code, target_productivity)
    
    if not metrics or 'weekly_data' not in metrics:
        raise HTTPException(status_code=404, detail="No data for project")
    
    img_base64 = plot_performance_chart(
        metrics['weekly_data'],
        target_productivity,
        project_code
    )
    
    return {"image": img_base64, "format": "png"}


@router.get("/chart/cumulative/{project_code}")
async def get_cumulative_chart(
    project_code: str,
    target_qty: float,
    start_year: int,
    end_year: int
):
    """Get cumulative progress chart as base64 image."""
    if perf_analyzer.df is None:
        raise HTTPException(status_code=400, detail="No data loaded")
    
    img_base64 = plot_cumulative_progress(
        perf_analyzer.df,
        project_code,
        target_qty,
        start_year,
        end_year
    )
    
    if not img_base64:
        raise HTTPException(status_code=404, detail="No data for project")
    
    return {"image": img_base64, "format": "png"}


@router.get("/cumulative-data/{project_code}")
async def get_cumulative_data(
    project_code: str,
    target_qty: float = None,
    start_year: int = None,
    end_year: int = None
):
    """Get cumulative progress data for charting."""
    import numpy as np
    from datetime import datetime
    
    if perf_analyzer.df is None:
        raise HTTPException(status_code=400, detail="No data loaded")
    
    # Filter for this project
    proj_df = perf_analyzer.df[perf_analyzer.df['Project'].str.upper() == project_code.upper()].copy()
    
    if proj_df.empty:
        raise HTTPException(status_code=404, detail=f"No data found for project {project_code}")
    
    # Get year range from data if not provided
    proj_df['Year'] = pd.to_numeric(proj_df['Year'], errors='coerce')
    proj_df = proj_df.dropna(subset=['Year'])
    
    data_start_year = int(proj_df['Year'].min())
    data_end_year = int(proj_df['Year'].max())
    current_year = datetime.now().year
    
    if start_year is None:
        start_year = data_start_year
    if end_year is None:
        end_year = max(data_end_year + 3, current_year + 3)  # Extend 3 years for projection
    
    # Calculate cumulative actual by year
    yearly_qty = proj_df.groupby('Year')['Qty Delivered'].sum().sort_index()
    cumulative_actual = yearly_qty.cumsum()
    
    # Get total actual so far
    total_actual = float(cumulative_actual.iloc[-1]) if len(cumulative_actual) > 0 else 0
    
    # If target_qty not provided, estimate from trend
    if target_qty is None:
        # Estimate target as 120% of current cumulative
        target_qty = total_actual * 1.2
    
    years = list(range(start_year, end_year + 1))
    total_years = len(years)
    
    # Calculate linear plan
    yearly_target = target_qty / total_years if total_years > 0 else 0
    
    # Calculate values needed for projections
    last_actual_year = int(cumulative_actual.index[-1]) if len(cumulative_actual) > 0 else start_year
    last_actual_value = float(cumulative_actual.iloc[-1]) if len(cumulative_actual) > 0 else 0
    
    # Calculate current pace (qty per year based on recent trend)
    if len(yearly_qty) >= 2:
        recent_years = yearly_qty.tail(3)
        current_pace = float(recent_years.mean())
    else:
        current_pace = float(yearly_qty.mean()) if len(yearly_qty) > 0 else 0
    
    # Calculate required speed to reach target
    remaining_years = end_year - last_actual_year
    remaining_qty = target_qty - last_actual_value
    required_speed = remaining_qty / remaining_years if remaining_years > 0 else 0
    
    # Calculate projected finish date
    if current_pace > 0:
        years_to_complete = remaining_qty / current_pace
        projected_finish_year = last_actual_year + years_to_complete
        month = int((years_to_complete % 1) * 12) + 1
        projected_finish = f"{int(projected_finish_year)}-{month:02d}-01"
    else:
        projected_finish = None
    
    # Build chart data - separate arrays for cleaner rendering
    chart_data = []
    
    for i, year in enumerate(years):
        point = {
            "year": year,
            "plan": round(yearly_target * (i + 1), 1),
            "actual": None,
            "recovery": None,
            "projected": None,
        }
        
        # Actual value (only for years with data, including all years up to last_actual_year)
        if year in cumulative_actual.index:
            point["actual"] = round(float(cumulative_actual[year]), 1)
        elif year < data_start_year:
            point["actual"] = 0  # Start from 0
        
        # Recovery path and Projected pace - only from last actual year onwards
        if year >= last_actual_year:
            years_from_last = year - last_actual_year
            
            # Recovery path (linear from current to target at end_year)
            if remaining_years > 0:
                recovery_value = last_actual_value + (remaining_qty * years_from_last / remaining_years)
                point["recovery"] = round(min(recovery_value, target_qty), 1)
            
            # Projected pace (based on current pace)
            projected_value = last_actual_value + (current_pace * years_from_last)
            point["projected"] = round(projected_value, 1)
        
        chart_data.append(point)
    
    return {
        "chart_data": chart_data,
        "metrics": {
            "current_pace": round(current_pace, 1),
            "required_speed": round(required_speed, 1),
            "projected_finish": projected_finish,
            "total_actual": round(total_actual, 1),
            "target_qty": round(target_qty, 1),
            "on_track": current_pace >= required_speed
        },
        "years": {
            "start": start_year,
            "end": end_year,
            "current": current_year,
            "last_actual": last_actual_year
        }
    }
