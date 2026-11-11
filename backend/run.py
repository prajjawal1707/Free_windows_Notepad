"""Backend entry point. Used by `python run.py` in dev and by PyInstaller in production."""
import argparse
import multiprocessing
import os
import sys
import threading
import time
from pathlib import Path

# A windowed PyInstaller build has no stdout/stderr; keep libraries from crashing.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import psutil  # noqa: E402
import uvicorn  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402


def _watch_parent(pid: int) -> None:
    """Exit if the desktop app dies, so we never leave an orphan server behind."""
    while True:
        time.sleep(2)
        if not psutil.pid_exists(pid):
            os._exit(0)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=settings.port)
    p.add_argument("--token", default=settings.token)
    p.add_argument("--data-dir", default=None)
    p.add_argument("--parent-pid", type=int, default=None)
    args = p.parse_args()

    settings.port = args.port
    settings.token = args.token
    if args.data_dir:
        settings.data_dir = Path(args.data_dir)
    if args.parent_pid:
        threading.Thread(target=_watch_parent, args=(args.parent_pid,), daemon=True).start()

    uvicorn.run(app, host=settings.host, port=settings.port, log_config=None)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
