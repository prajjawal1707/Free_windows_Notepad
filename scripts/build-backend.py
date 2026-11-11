#!/usr/bin/env python3
"""Package the FastAPI backend with PyInstaller and place it where Tauri expects the sidecar.

Usage:
  python scripts/build-backend.py                # real build for this machine
  python scripts/build-backend.py --placeholder  # empty stub so `tauri dev` compiles
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
BIN_DIR = ROOT / "src-tauri" / "binaries"


def target_triple() -> str:
    out = subprocess.run(["rustc", "-vV"], capture_output=True, text=True, check=True).stdout
    return re.search(r"^host: (.+)$", out, re.M).group(1).strip()


def main() -> None:
    triple = target_triple()
    ext = ".exe" if "windows" in triple else ""
    dest = BIN_DIR / f"backend-{triple}{ext}"
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    if "--placeholder" in sys.argv:
        if not dest.exists():
            dest.write_bytes(b"")
            dest.chmod(0o755)
        print(f"Placeholder created: {dest}")
        return

    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--onefile", "--noconfirm", "--clean", "--name", "backend",
         "--collect-submodules", "uvicorn", "--collect-submodules", "app",
         "--distpath", str(BACKEND / "dist"), "--workpath", str(BACKEND / "build"),
         "--specpath", str(BACKEND / "build"), "run.py"],
        cwd=BACKEND, check=True,
    )
    built = BACKEND / "dist" / f"backend{ext}"
    shutil.copy2(built, dest)
    print(f"Sidecar ready: {dest}")


if __name__ == "__main__":
    main()
