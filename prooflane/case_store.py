"""Additive case storage with optimistic revisions; existing run data is untouched."""
import json
import time


class StaleCase(ValueError):
    pass


class CaseStore:
    def __init__(self, store):
        self.store = store
        with store.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, owner TEXT NOT NULL, created REAL NOT NULL, revision INTEGER NOT NULL, body TEXT NOT NULL)")
            db.execute("CREATE INDEX IF NOT EXISTS cases_owner ON cases(owner,created)")

    @staticmethod
    def prune(db):
        db.execute("DELETE FROM cases WHERE created < ?", (time.time() - 86400,))

    def add(self, owner, case):
        with self.store.connect() as db:
            self.prune(db)
            if db.execute("SELECT count(*) FROM cases").fetchone()[0] >= 200:
                raise ValueError("Case storage quota reached.")
            db.execute("INSERT INTO cases VALUES (?,?,?,?,?)", (case["id"], owner, time.time(), case["revision"], json.dumps(case)))

    def list(self, owner):
        with self.store.connect() as db:
            self.prune(db)
            return [json.loads(r[0]) for r in db.execute("SELECT body FROM cases WHERE owner=? ORDER BY created DESC LIMIT 30", (owner,))]

    def get(self, owner, case_id):
        with self.store.connect() as db:
            self.prune(db)
            row = db.execute("SELECT body FROM cases WHERE id=? AND owner=?", (case_id, owner)).fetchone()
            return json.loads(row[0]) if row else None

    def update(self, owner, case, expected_revision):
        new_case = {**case, "revision": expected_revision + 1}
        with self.store.connect() as db:
            self.prune(db)
            cursor = db.execute("UPDATE cases SET revision=?, body=? WHERE id=? AND owner=? AND revision=?",
                                (new_case["revision"], json.dumps(new_case), case["id"], owner, expected_revision))
            if cursor.rowcount != 1:
                raise StaleCase("The case changed or expired. Reopen it before editing.")
        return new_case
