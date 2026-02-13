# MTR DUAT - Parse Router
"""DOCX parsing API endpoints."""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import tempfile
import shutil
from pathlib import Path
import sys
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from parsers.docx_parser import DailyReportParser, process_docx

logger = logging.getLogger(__name__)

router = APIRouter()

# Import shared state from services
from backend.services import parsing_state


class FolderParseRequest(BaseModel):
    folder_path: str


class ParseResult(BaseModel):
    success: bool
    total_records: int
    max_week: int
    records: List[Dict[str, Any]]


@router.post("/docx")
async def parse_single_docx(file: UploadFile = File(...)):
    """Parse a single DOCX file and extract records."""
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="File must be a .docx file")
    
    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    
    try:
        records = process_docx(tmp_path)
        return {
            "success": True,
            "filename": file.filename,
            "total_records": len(records),
            "records": records
        }
    except Exception as e:
        logger.error("Failed to parse DOCX: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        tmp_path.unlink(missing_ok=True)


@router.post("/folder")
async def parse_folder(request: FolderParseRequest, background_tasks: BackgroundTasks):
    """
    Parse all daily reports in a folder.
    Returns immediately and processing happens in background.
    Poll /progress endpoint for status.
    """
    folder_path = Path(request.folder_path)
    
    if not folder_path.exists():
        raise HTTPException(status_code=400, detail="Folder does not exist")
    
    if not folder_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a directory")
    
    # Check if already processing
    if parsing_state["in_progress"]:
        raise HTTPException(status_code=409, detail="Parsing already in progress")
    
    # Start background parsing
    background_tasks.add_task(process_folder_background, folder_path)
    
    return {"status": "started", "message": "Parsing started in background"}


def process_folder_background(folder_path: Path):
    """Background task to process folder."""
    global parsing_state
    
    parsing_state["in_progress"] = True
    parsing_state["progress"] = 0
    parsing_state["records"] = []
    
    parser = DailyReportParser(folder_path)
    files = parser.get_report_files()
    
    parsing_state["total_files"] = len(files)
    
    def progress_callback(filename: str, progress: float):
        parsing_state["current_file"] = filename
        parsing_state["progress"] = progress
    
    try:
        records = parser.process_all(progress_callback)
        parsing_state["records"] = records
        parsing_state["max_week"] = parser.get_max_week()
        parsing_state["progress"] = 1.0
    except Exception as e:
        logger.error("Background folder parsing failed: %s", e)
        parsing_state["error"] = str(e)
    finally:
        parsing_state["in_progress"] = False


@router.get("/progress")
async def get_parse_progress():
    """Get current parsing progress."""
    return {
        "in_progress": parsing_state["in_progress"],
        "progress": parsing_state["progress"],
        "current_file": parsing_state["current_file"],
        "total_files": parsing_state["total_files"],
        "records_count": len(parsing_state["records"]),
        "max_week": parsing_state["max_week"],
        "error": parsing_state.get("error")
    }


@router.get("/results")
async def get_parse_results():
    """Get parsing results after completion."""
    if parsing_state["in_progress"]:
        raise HTTPException(status_code=409, detail="Parsing still in progress")
    
    return {
        "success": True,
        "total_records": len(parsing_state["records"]),
        "max_week": parsing_state["max_week"],
        "records": parsing_state["records"]
    }


@router.get("/files")
async def list_report_files(folder_path: str):
    """List all daily report files in a folder."""
    path = Path(folder_path)
    
    if not path.exists() or not path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid folder path")
    
    parser = DailyReportParser(path)
    files = parser.get_report_files()
    
    return {
        "folder": str(path),
        "total_files": len(files),
        "files": [f.name for f in files]
    }
