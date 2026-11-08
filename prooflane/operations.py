"""Bounded, session-owned records for recovering a mutation without executing it twice.

Only identities and a request digest are persisted here, never source bodies or
operator credentials. The service runs one application worker; pending work from
a previous startup is reconciled, never automatically restarted.
"""
import threading
import time


class OperationConflict(ValueError):
    pass


class OperationStore:
    def __init__(self, store, cases):
        self.store = store
        with store.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS operations (
                owner TEXT NOT NULL, id TEXT NOT NULL, created REAL NOT NULL,
                scope TEXT NOT NULL, fingerprint TEXT NOT NULL, status TEXT NOT NULL,
                case_id TEXT, failed_run_id TEXT, http_status INTEGER NOT NULL,
                error TEXT, PRIMARY KEY(owner,id))""")
            db.execute("CREATE INDEX IF NOT EXISTS operations_created ON operations(created)")
            pending = db.execute("SELECT owner,id,scope,case_id FROM operations WHERE status='pending'").fetchall()
        # Reconcile the narrow crash window after committing a case mutation but
        # before completing its operation record. No program is rerun.
        for owner, operation_id, scope, case_id in pending:
            case = cases.get(owner, case_id) if case_id else None
            committed = bool(case and (scope == "create" or any(
                variant.get("request_id") == operation_id for variant in case["variants"])))
            self.finish(owner, operation_id, "completed" if committed else "interrupted", case_id=case_id,
                        http_status=200 if committed else 409,
                        error=None if committed else "The service restarted before completion was confirmed. This request will not execute again. Inspect the archive before starting a new request.")

    @staticmethod
    def _prune(db):
        db.execute("DELETE FROM operations WHERE created < ?", (time.time() - 86400,))

    @staticmethod
    def _value(row):
        if not row:
            return None
        keys = ("id", "status", "case_id", "failed_run_id", "http_status", "error")
        return {key: value for key, value in zip(keys, row) if value is not None}

    def get(self, owner, operation_id):
        with self.store.connect() as db:
            self._prune(db)
            return self._value(db.execute("SELECT id,status,case_id,failed_run_id,http_status,error FROM operations WHERE owner=? AND id=?",
                                          (owner, operation_id)).fetchone())

    def begin(self, owner, operation_id, scope, fingerprint, case_id):
        with self.store.connect() as db:
            # Reserve before an external or sandbox call. SQLite serializes this
            # tiny transaction; no database lock spans the actual execution.
            db.execute("BEGIN IMMEDIATE")
            self._prune(db)
            old = db.execute("SELECT scope,fingerprint FROM operations WHERE owner=? AND id=?", (owner, operation_id)).fetchone()
            if old:
                if old != (scope, fingerprint):
                    raise OperationConflict("This request ID was already used with different inputs. Use a new request ID for an intentional new operation.")
                row = db.execute("SELECT id,status,case_id,failed_run_id,http_status,error FROM operations WHERE owner=? AND id=?", (owner, operation_id)).fetchone()
                return self._value(row), False
            if db.execute("SELECT count(*) FROM operations").fetchone()[0] >= 2000 or db.execute(
                    "SELECT count(*) FROM operations WHERE owner=?", (owner,)).fetchone()[0] >= 120:
                raise OperationConflict("Operation recovery storage is full. Wait for earlier records to expire.")
            db.execute("INSERT INTO operations VALUES (?,?,?,?,?,'pending',?,NULL,202,NULL)",
                       (owner, operation_id, time.time(), scope, fingerprint, case_id))
        return {"id": operation_id, "status": "pending", "case_id": case_id, "http_status": 202}, True

    def finish(self, owner, operation_id, status, case_id=None, failed_run_id=None, http_status=200, error=None):
        with self.store.connect() as db:
            db.execute("UPDATE operations SET status=?,case_id=?,failed_run_id=?,http_status=?,error=? WHERE owner=? AND id=?",
                       (status, case_id, failed_run_id, http_status, error, owner, operation_id))
        return self.get(owner, operation_id)


class CaseLocks:
    """Only active case mutations occupy the bounded set; no idle lock cache."""
    def __init__(self, maximum=128):
        self.maximum = maximum
        self.guard = threading.Lock()
        self.active = set()

    def acquire(self, owner, case_id):
        key = (owner, case_id)
        with self.guard:
            if key in self.active or len(self.active) >= self.maximum:
                return False
            self.active.add(key)
            return True

    def release(self, owner, case_id):
        with self.guard:
            self.active.discard((owner, case_id))
