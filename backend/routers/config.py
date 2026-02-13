# MTR DUAT - Config Router
"""Configuration management API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sys
from pathlib import Path

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
async def browse_directory(path: str = "C:\\"):
    """Open native Windows folder picker dialog via subprocess."""
    import asyncio, subprocess, sys, tempfile, os
    import logging
    logger = logging.getLogger(__name__)
    
    result_file = tempfile.mktemp(suffix='.txt')
    error_file = tempfile.mktemp(suffix='.err.txt')
    
    # Sanitize path - ensure trailing backslash doesn't break string literal
    safe_path = path.replace("\\", "/")
    
    script = f'''import sys, traceback
try:
    import tkinter as tk
    from tkinter import filedialog
    import ctypes

    ctypes.windll.user32.SetProcessDPIAware()
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("0x0+0+0")
    root.attributes("-topmost", True)
    root.update()
    root.focus_force()

    folder = filedialog.askdirectory(
        initialdir="{safe_path}",
        title="Select Folder",
        parent=root
    )
    root.destroy()

    with open(r"{result_file}", "w") as f:
        f.write(folder if folder else "")
except Exception as e:
    with open(r"{error_file}", "w") as f:
        f.write(traceback.format_exc())
'''
    tmp_script = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    tmp_script.write(script)
    tmp_script.close()
    
    try:
        # Always use python.exe (not pythonw) so tkinter GUI works
        python_exe = sys.executable
        logger.info(f"Browse: using python={python_exe}, script={tmp_script.name}")
        
        loop = asyncio.get_event_loop()
        
        def run_dialog():
            proc = subprocess.Popen(
                [python_exe, tmp_script.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate(timeout=120)
            if stderr:
                logger.warning(f"Browse dialog stderr: {stderr.decode()}")
            return proc.returncode
        
        returncode = await loop.run_in_executor(None, run_dialog)
        logger.info(f"Browse: subprocess returned {returncode}")
        
        # Check for errors
        if os.path.exists(error_file):
            with open(error_file, 'r') as f:
                err = f.read().strip()
            os.unlink(error_file)
            if err:
                logger.error(f"Browse dialog error: {err}")
                raise HTTPException(status_code=500, detail=err)
        
        selected = ""
        if os.path.exists(result_file):
            with open(result_file, 'r') as f:
                selected = f.read().strip()
            os.unlink(result_file)
        
        if selected:
            selected = selected.replace("/", "\\")
            return {"selected": selected}
        return {"selected": ""}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Browse exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_script.name):
            try: os.unlink(tmp_script.name)
            except: pass
        if os.path.exists(result_file):
            try: os.unlink(result_file)
            except: pass
        if os.path.exists(error_file):
            try: os.unlink(error_file)
            except: pass
