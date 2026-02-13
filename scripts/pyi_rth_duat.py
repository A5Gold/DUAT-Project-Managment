"""
Runtime hook for PyInstaller.
Ensures sys.path includes the correct directories for the frozen backend.
"""
import os
import sys
from pathlib import Path

# In frozen mode, add the _internal directory to sys.path
# so that 'routers', 'analysis', 'parsers', 'config', 'utils' can be found
if getattr(sys, 'frozen', False):
    bundle_dir = Path(sys._MEIPASS)
    backend_dir = bundle_dir / 'backend'

    for p in [str(bundle_dir), str(backend_dir)]:
        if p not in sys.path:
            sys.path.insert(0, p)
