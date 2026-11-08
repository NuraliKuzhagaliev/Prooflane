import json
import sqlite3
import time
from pathlib import Path


class Store:
    def __init__(self, directory):
        self.path = Path(directory) / "prooflane.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, owner TEXT NOT NULL, created REAL NOT NULL, run TEXT NOT NULL, receipt TEXT)")
            db.execute("CREATE INDEX IF NOT EXISTS runs_owner ON runs(owner,created)")

    def connect(self):
        return sqlite3.connect(self.path, timeout=5)

    def add(self, owner, run, receipt):
        with self.connect() as db:
            db.execute("DELETE FROM runs WHERE created < ?", (time.time() - 86400,))
            if db.execute("SELECT count(*) FROM runs").fetchone()[0] >= 1000:
                raise RuntimeError("Server storage quota reached. Try later.")
            db.execute("INSERT INTO runs VALUES (?,?,?,?,?)", (run["id"], owner, time.time(), json.dumps(run), json.dumps(receipt) if receipt else None))

    def list(self, owner):
        with self.connect() as db:
            db.execute("DELETE FROM runs WHERE created < ?", (time.time() - 86400,))
            return [json.loads(r[0]) for r in db.execute("SELECT run FROM runs WHERE owner=? AND created>? ORDER BY created DESC LIMIT 30", (owner, time.time()-86400))]

    def get(self, owner, run_id, receipt=False):
        with self.connect() as db:
            db.execute("DELETE FROM runs WHERE created < ?", (time.time() - 86400,))
            row = db.execute("SELECT run,receipt FROM runs WHERE owner=? AND id=? AND created>?", (owner, run_id, time.time()-86400)).fetchone()
        return json.loads(row[int(receipt)]) if row and row[int(receipt)] else None
