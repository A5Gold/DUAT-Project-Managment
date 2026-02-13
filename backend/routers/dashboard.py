# MTR DUAT - Dashboard Router
"""Dashboard analysis API endpoints."""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import tempfile
import shutil
from pathlib import Path
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from analysis.dashboard import (
    DashboardAnalyzer,
    aggregate_records,
    calculate_summary,
    get_weekly_trend,
    get_monthly_trend,
    get_project_distribution,
    get_keyword_distribution
)


def convert_to_native(obj):
    """Convert numpy/pandas types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif pd.isna(obj):
        return None
    else:
        return obj

router = APIRouter()

# Global analyzer instance
analyzer = DashboardAnalyzer()


class RecordsInput(BaseModel):
    records: List[Dict[str, Any]]
    max_week: Optional[int] = None


@router.post("/analyze")
async def analyze_records(input_data: RecordsInput):
    """Analyze records and generate dashboard data."""
    if not input_data.records:
        raise HTTPException(status_code=400, detail="No records provided")
    
    success = analyzer.load_from_records(input_data.records, input_data.max_week)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to analyze records")
    
    return convert_to_native({
        "success": True,
        "stats": analyzer.get_stats(),
        "last_updated": analyzer.last_updated
    })


@router.post("/load-excel")
async def load_from_excel(file: UploadFile = File(...)):
    """Load dashboard data from an existing Excel file."""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be an Excel file")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    
    try:
        success = analyzer.load_from_excel(tmp_path)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to load Excel file")
        
        return convert_to_native({
            "success": True,
            "filename": file.filename,
            "stats": analyzer.get_stats(),
            "last_updated": analyzer.last_updated
        })
    finally:
        tmp_path.unlink(missing_ok=True)


@router.get("/stats")
async def get_stats():
    """Get summary statistics."""
    stats = analyzer.get_stats()
    if not stats:
        raise HTTPException(status_code=404, detail="No data loaded")
    return convert_to_native(stats)


@router.get("/summary")
async def get_summary():
    """Get project summary table."""
    if analyzer.summary is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    return convert_to_native({
        "columns": analyzer.summary.columns.tolist(),
        "data": analyzer.summary.to_dict(orient="records")
    })


@router.get("/trends/weekly")
async def get_weekly_trends(weeks: int = 12):
    """Get weekly trend data for charts."""
    if analyzer.df is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    week_labels, category_data = get_weekly_trend(analyzer.df, weeks)
    
    return convert_to_native({
        "labels": week_labels,
        "datasets": category_data
    })


@router.get("/trends/monthly")
async def get_monthly_trends(months: int = 6):
    """Get monthly trend data."""
    if analyzer.df is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    month_labels, nth_counts = get_monthly_trend(analyzer.df, months)
    
    return convert_to_native({
        "labels": month_labels,
        "data": nth_counts
    })


@router.get("/distribution/projects")
async def get_projects_distribution():
    """Get NTH distribution by project."""
    if analyzer.df is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    distribution = get_project_distribution(analyzer.df)
    
    return convert_to_native({
        "labels": list(distribution.keys()),
        "data": list(distribution.values())
    })


@router.get("/distribution/keywords")
async def get_keywords_distribution():
    """Get NTH distribution by keyword jobs."""
    if analyzer.df is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    distribution = get_keyword_distribution(analyzer.df)
    
    return convert_to_native({
        "labels": list(distribution.keys()),
        "data": list(distribution.values())
    })


@router.get("/raw-data")
async def get_raw_data(limit: int = 100, offset: int = 0):
    """Get raw data with pagination."""
    if analyzer.df is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    total = len(analyzer.df)
    data = analyzer.df.iloc[offset:offset + limit]
    
    return convert_to_native({
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": data.to_dict(orient="records")
    })


@router.get("/pivot")
async def get_nth_pivot():
    """Get NTH pivot table by week and project."""
    if analyzer.nth_trend is None or analyzer.nth_trend.empty:
        raise HTTPException(status_code=404, detail="No trend data available")
    
    pivot = analyzer.nth_trend.reset_index()
    
    return convert_to_native({
        "columns": pivot.columns.tolist(),
        "data": pivot.to_dict(orient="records")
    })


@router.get("/distribution/lines")
async def get_line_distribution():
    """Get NTH and Qty distribution by rail line."""
    if analyzer.df is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    df = analyzer.df
    if 'Line' not in df.columns:
        return convert_to_native({
            "labels": [],
            "nth_data": [],
            "qty_data": []
        })
    
    df_with_line = df[df['Line'] != ''].copy()
    if df_with_line.empty:
        return convert_to_native({
            "labels": [],
            "nth_data": [],
            "qty_data": []
        })
    
    # NTH by line
    line_nth = df_with_line.groupby('Line').size()
    # Qty by line
    line_qty = df_with_line.groupby('Line')['Qty Delivered'].sum() if 'Qty Delivered' in df_with_line.columns else pd.Series()
    
    # Sort by NTH descending
    sorted_lines = line_nth.sort_values(ascending=False)
    
    return convert_to_native({
        "labels": sorted_lines.index.tolist(),
        "nth_data": sorted_lines.values.tolist(),
        "qty_data": [line_qty.get(line, 0) for line in sorted_lines.index]
    })


@router.get("/trends/nth-by-project")
async def get_nth_trend_by_project(weeks: int = 52):
    """Get NTH trend by week for all projects."""
    if analyzer.nth_trend is None or analyzer.nth_trend.empty:
        raise HTTPException(status_code=404, detail="No trend data available")
    
    # Get last N weeks
    trend_data = analyzer.nth_trend.tail(weeks)
    
    # Get week labels (index)
    week_labels = trend_data.index.tolist()
    
    # Get project columns sorted by total NTH
    project_totals = trend_data.sum().sort_values(ascending=False)
    projects = project_totals.index.tolist()
    
    # Build datasets for each project
    datasets = {}
    for proj in projects:
        if proj in trend_data.columns:
            datasets[proj] = trend_data[proj].fillna(0).tolist()
    
    return convert_to_native({
        "labels": week_labels,
        "projects": projects,
        "datasets": datasets,
        "totals": project_totals.to_dict()
    })
