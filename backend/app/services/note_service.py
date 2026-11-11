import csv
import io
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Note
from app.repositories import note_repo

COLUMNS = ["title", "content", "tags", "pinned", "created_at", "updated_at"]
MAX_IMPORT_ROWS = 5000
_FORMULA_START = ("=", "+", "@", "\t", "\r")


def _safe(cell: str) -> str:
    """Stop Excel from treating note text as a formula."""
    return "'" + cell if cell.startswith(_FORMULA_START) else cell


def _unsafe(cell: str) -> str:
    return cell[1:] if cell.startswith("'") and cell[1:].startswith(_FORMULA_START) else cell


def export_csv(notes: List[Note]) -> Path:
    out_dir = settings.exports_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"notes-{datetime.now():%Y%m%d-%H%M%S}.csv"
    # utf-8-sig so Excel opens non-English text correctly
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for n in notes:
            w.writerow([_safe(n.title), _safe(n.content), _safe(n.tags), "yes" if n.pinned else "no",
                        n.created_at.isoformat(sep=" ", timespec="seconds"),
                        n.updated_at.isoformat(sep=" ", timespec="seconds")])
    return path


def import_csv(db: Session, user_id: int, text: str) -> int:
    text = text.lstrip("\ufeff")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if not reader.fieldnames:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The file is empty")
    fields = {(h or "").strip().lower(): h for h in reader.fieldnames}
    if "title" not in fields and "content" not in fields:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "CSV needs a header row with a 'title' and/or 'content' column")

    def get(row, name: str) -> str:
        key = fields.get(name)
        return _unsafe((row.get(key) or "").strip()) if key else ""

    rows = []
    for i, row in enumerate(reader):
        if i >= MAX_IMPORT_ROWS:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Too many rows (max {MAX_IMPORT_ROWS})")
        title, content = get(row, "title")[:200], get(row, "content")
        if not title and not content:
            continue
        rows.append({
            "title": title, "content": content[:200000], "tags": get(row, "tags")[:256],
            "pinned": get(row, "pinned").lower() in ("1", "true", "yes", "y"),
        })
    if not rows:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No notes found in the file")
    return note_repo.add_many(db, user_id, rows)
