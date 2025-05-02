# ==== FastAPI side (Python 3.10+) ==================================
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import sqlite3, datetime, os

DB = "files.db"
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI(title="File Manager")

class FileEntry(BaseModel):
    id: int | None = None
    filename: str
    timestamp: str
    dir: str

# ---------- init & seed ------------
def init_db():
    conn = sqlite3.connect(DB)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS file("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "filename TEXT, timestamp TEXT, dir TEXT)"
    )
    conn.commit()
    # まだ行が無ければ 100 ファイル生成
    cur = conn.execute("SELECT COUNT(*) FROM file")
    if cur.fetchone()[0] == 0:
        for i in range(100):
            name = f"dummy_{i:03d}.txt"
            (DATA_DIR / name).touch()
            conn.execute(
                "INSERT INTO file(filename,timestamp,dir) VALUES(?,?,?)",
                (name, datetime.datetime.utcnow().isoformat(), str(DATA_DIR)),
            )
    conn.commit(); conn.close()

init_db()

# ---------- API --------------------
@app.get("/api/files", response_model=list[FileEntry])
def list_files():
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT id,filename,timestamp,dir FROM file").fetchall()
    conn.close()
    return [FileEntry(id=r[0], filename=r[1], timestamp=r[2], dir=r[3]) for r in rows]

@app.put("/api/file/{file_id}", response_model=FileEntry)
def rename_file(file_id: int, new_name: str):
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT filename, dir FROM file WHERE id=?", (file_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="File not found")
    old_path = Path(row[1]) / row[0]
    new_path = old_path.with_name(new_name)
    if new_path.exists():
        raise HTTPException(status_code=400, detail="Name already exists")
    os.rename(old_path, new_path)
    conn.execute(
        "UPDATE file SET filename=?, timestamp=? WHERE id=?",
        (new_name, datetime.datetime.utcnow().isoformat(), file_id),
    )
    conn.commit()
    cur = conn.execute("SELECT id,filename,timestamp,dir FROM file WHERE id=?", (file_id,))
    r = cur.fetchone(); conn.close()
    return FileEntry(id=r[0], filename=r[1], timestamp=r[2], dir=r[3])