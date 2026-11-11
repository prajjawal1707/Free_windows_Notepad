import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

APP_VERSION = "1.0.0"


def _default_data_dir() -> Path:
    return Path(os.environ.get("APP_DATA_DIR", Path.home() / ".my-desktop-app"))


@dataclass
class Settings:
    host: str = "127.0.0.1"          # never bind to anything but loopback
    port: int = 8765                 # overridden by --port in production
    token: str = "dev-token"         # per-launch secret, overridden by --token
    data_dir: Path = field(default_factory=_default_data_dir)
    parent_pid: Optional[int] = None  # desktop app PID; backend exits if it dies
    export_dir: Optional[Path] = None  # where CSV exports go (default: ~/Downloads)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "app.db"

    @property
    def exports_dir(self) -> Path:
        return self.export_dir or (Path.home() / "Downloads")

    @property
    def log_dir(self) -> Path:
        return self.data_dir / "logs"


settings = Settings()

ALLOWED_ORIGINS = [
    "tauri://localhost",
    "http://tauri.localhost",
    "https://tauri.localhost",
    "http://localhost:1420",   # Vite dev server
    "http://127.0.0.1:1420",
]
