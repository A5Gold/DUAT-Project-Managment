"""
MTR DUAT - Complete Build Script

Automates the full build pipeline:
  1. Run backend tests (pytest)
  2. Run frontend tests (vitest)
  3. Run electron tests (vitest)
  4. Build frontend (vite build)
  5. Build backend (PyInstaller)
  6. Build Electron portable .exe (electron-builder)

Usage:
    python scripts/build.py              # Full build
    python scripts/build.py --skip-tests # Skip test phase
    python scripts/build.py --backend-only  # PyInstaller only
    python scripts/build.py --frontend-only # Vite build only
    python scripts/build.py --electron-only # electron-builder only
"""

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("build")

ROOT = Path(__file__).parent.parent
BACKEND_DIST = ROOT / "backend_dist"
FRONTEND_DIST = ROOT / "frontend" / "dist"
BUILD_OUTPUT = ROOT / "build"


def run_command(cmd: list[str], cwd: Path | None = None, label: str = "") -> bool:
    """Run a subprocess command and return True on success."""
    display = label or " ".join(cmd)
    logger.info("Running: %s", display)
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or ROOT,
            check=True,
            capture_output=False,
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error("FAILED: %s (exit code %d)", display, e.returncode)
        return False
    except FileNotFoundError:
        logger.error("Command not found: %s", cmd[0])
        return False


def clean_build_artifacts() -> None:
    """Remove previous build artifacts."""
    logger.info("Cleaning previous build artifacts...")
    for d in [BACKEND_DIST, BUILD_OUTPUT]:
        if d.exists():
            shutil.rmtree(d)
            logger.info("  Removed %s", d)


def run_backend_tests() -> bool:
    """Run pytest with coverage."""
    logger.info("=" * 60)
    logger.info("Phase 1: Backend Tests")
    logger.info("=" * 60)
    return run_command(
        [sys.executable, "-m", "pytest", "tests/", "--cov", "--cov-report=term-missing", "-q"],
        label="pytest (backend)",
    )


def run_frontend_tests() -> bool:
    """Run frontend vitest."""
    logger.info("=" * 60)
    logger.info("Phase 2: Frontend Tests")
    logger.info("=" * 60)
    return run_command(
        ["npm", "run", "test"],
        cwd=ROOT / "frontend",
        label="vitest (frontend)",
    )


def run_electron_tests() -> bool:
    """Run electron vitest."""
    logger.info("=" * 60)
    logger.info("Phase 3: Electron Tests")
    logger.info("=" * 60)
    return run_command(
        ["npx", "vitest", "--run", "--config", "electron/vitest.config.js"],
        label="vitest (electron)",
    )


def build_frontend() -> bool:
    """Build the React SPA with Vite."""
    logger.info("=" * 60)
    logger.info("Phase 4: Frontend Build (Vite)")
    logger.info("=" * 60)
    return run_command(
        ["npm", "run", "build"],
        cwd=ROOT / "frontend",
        label="vite build",
    )


def build_backend() -> bool:
    """Build the FastAPI backend with PyInstaller."""
    logger.info("=" * 60)
    logger.info("Phase 5: Backend Build (PyInstaller)")
    logger.info("=" * 60)
    spec_file = ROOT / "backend.spec"
    if not spec_file.exists():
        logger.error("backend.spec not found at %s", spec_file)
        return False
    return run_command(
        [
            sys.executable, "-m", "PyInstaller",
            str(spec_file),
            "--distpath", str(BACKEND_DIST),
            "--clean",
            "--noconfirm",
        ],
        label="pyinstaller backend.spec",
    )


def build_electron() -> bool:
    """Build the Electron portable .exe."""
    logger.info("=" * 60)
    logger.info("Phase 6: Electron Build (electron-builder)")
    logger.info("=" * 60)

    if not FRONTEND_DIST.exists():
        logger.error("frontend/dist/ not found. Run frontend build first.")
        return False

    backend_exe = BACKEND_DIST / "backend" / "backend.exe"
    if not backend_exe.exists():
        logger.error("backend_dist/backend/backend.exe not found. Run backend build first.")
        return False

    return run_command(
        ["npx", "electron-builder", "--win", "--config", "electron-builder.yml"],
        label="electron-builder --win",
    )


def verify_output() -> bool:
    """Verify the build output exists."""
    logger.info("=" * 60)
    logger.info("Verification")
    logger.info("=" * 60)

    exe_pattern = list(BUILD_OUTPUT.glob("MTR_DUAT_*.exe"))
    if exe_pattern:
        exe_path = exe_pattern[0]
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        logger.info("SUCCESS: %s (%.1f MB)", exe_path.name, size_mb)
        return True

    logger.error("No .exe found in %s", BUILD_OUTPUT)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="MTR DUAT Build Script")
    parser.add_argument("--skip-tests", action="store_true", help="Skip test phase")
    parser.add_argument("--skip-clean", action="store_true", help="Skip cleaning artifacts")
    parser.add_argument("--backend-only", action="store_true", help="PyInstaller build only")
    parser.add_argument("--frontend-only", action="store_true", help="Vite build only")
    parser.add_argument("--electron-only", action="store_true", help="electron-builder only")
    args = parser.parse_args()

    logger.info("MTR DUAT Build Pipeline v4.0.0")
    logger.info("Root: %s", ROOT)

    # Partial builds
    if args.backend_only:
        return 0 if build_backend() else 1
    if args.frontend_only:
        return 0 if build_frontend() else 1
    if args.electron_only:
        return 0 if build_electron() else 1

    # Full build pipeline
    if not args.skip_clean:
        clean_build_artifacts()

    if not args.skip_tests:
        if not run_backend_tests():
            logger.error("Backend tests failed. Aborting build.")
            return 1
        if not run_frontend_tests():
            logger.error("Frontend tests failed. Aborting build.")
            return 1
        if not run_electron_tests():
            logger.error("Electron tests failed. Aborting build.")
            return 1

    if not build_frontend():
        logger.error("Frontend build failed.")
        return 1

    if not build_backend():
        logger.error("Backend build failed.")
        return 1

    if not build_electron():
        logger.error("Electron build failed.")
        return 1

    if not verify_output():
        return 1

    logger.info("=" * 60)
    logger.info("BUILD COMPLETE")
    logger.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
