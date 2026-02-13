# MTR DUAT - Config Router
"""Configuration management API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import load_app_config, save_app_config, DEFAULT_CONFIG

router = APIRouter()


class ConfigUpdate(BaseModel):
    last_folder: Optional[str] = None
    language: Optional[str] = None
    dark_mode: Optional[bool] = None
    default_productivity: Optional[float] = None
    keywords: Optional[List[str]] = None


@router.get("")
async def get_config():
    """Get current application configuration."""
    config = load_app_config()
    return config


@router.put("")
async def update_config(update: ConfigUpdate):
    """Update application configuration."""
    config = load_app_config()
    
    # Update only provided fields
    if update.last_folder is not None:
        config["last_folder"] = update.last_folder
    if update.language is not None:
        config["language"] = update.language
    if update.dark_mode is not None:
        config["dark_mode"] = update.dark_mode
    if update.default_productivity is not None:
        config["default_productivity"] = update.default_productivity
    if update.keywords is not None:
        config["keywords"] = update.keywords
    
    success = save_app_config(config)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save configuration")
    
    return {"status": "ok", "config": config}


@router.post("/reset")
async def reset_config():
    """Reset configuration to defaults."""
    success = save_app_config(DEFAULT_CONFIG.copy())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reset configuration")
    
    return {"status": "ok", "config": DEFAULT_CONFIG}

@router.get("/browse")
async def browse_directory():
    """Folder selection is handled by Electron native dialog via IPC.

    This endpoint is kept for API compatibility but should not be called
    directly. The React frontend uses ``window.electronAPI.openDirectory()``
    which invokes the native OS dialog through Electron's main process.
    """
    raise HTTPException(
        status_code=501,
        detail="Use Electron IPC dialog:openDirectory instead",
    )
