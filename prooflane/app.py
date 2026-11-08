import inspect
import json
import os
import re
import secrets
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import __version__
from .analysis import InputError, canonical, contract_output, digest, parse_csv, summarize, verify_output
from .comparison import apply_assumption, compare_receipts, make_bundle
from .case_api import register_case_routes
from .provider import ProviderError, VultrProvider
from .receipts import make_receipt
from .recipe import RECIPE
from .sandbox import DockerSandbox, SandboxError
from .store import Store

ROOT = Path(__file__).resolve().parents[1]


def load_local_config():
    """Only a project-local config; never log values or overwrite process configuration."""
    config = ROOT / ".env"
    if config.exists():
        for line in config.read_text(encoding="utf-8-sig").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                name, value = line.split("=", 1)
                if name.strip() in {"VULTR_INFERENCE_API_KEY", "VULTR_MODEL", "PROOFLANE_OPERATOR_TOKEN",
                                    "PROOFLANE_LIVE_ENABLED", "PROOFLANE_PUBLIC_ORIGIN",
                                    "PROOFLANE_SANDBOX_IMAGE", "PROOFLANE_DATA_DIR"}:
                    os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    csv: str = Field(min_length=1, max_length=131072)
    filename: str = Field(default="invoices.csv", min_length=1, max_length=100)
    question: str = Field(default="Find positive differences against contract prices and cite each source record.", min_length=1, max_length=600)
    mode: str = Field(default="reference", pattern="^(reference|sandbox|vultr)$")
    operator_token: str = Field(default="", max_length=256)

    @field_validator("filename", "question", "operator_token")
    @classmethod
    def valid_text(cls, value):
        try:
            value.encode("utf-8")
        except UnicodeError as exc:
            raise ValueError("Text must be valid UTF-8.") from exc
        return value


class Limiter:
    def __init__(self):
        self.lock = threading.Lock()
        self.entries = {}

    def take(self, key, maximum, period=3600):
        now = time.monotonic()
        with self.lock:
            self.entries = {k: (until, count) for k, (until, count) in self.entries.items() if until > now}
            until, count = self.entries.get(key, (now + period, 0))
            if count >= maximum or len(self.entries) >= 2000:
                raise HTTPException(429, "Run quota reached. Please try again later.")
            self.entries[key] = (until, count + 1)


class ScenarioRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    baseline_receipt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    row: int = Field(strict=True, ge=2, le=501)
    field: Literal["quantity", "unit_price", "contract_price"]
    value: str = Field(min_length=1, max_length=32)
    operator_token: str = Field(default="", max_length=256)

    @field_validator("value", "operator_token")
    @classmethod
    def valid_text(cls, value):
        try:
            value.encode("utf-8")
        except UnicodeError as exc:
            raise ValueError("Text must be valid UTF-8.") from exc
        return value


def create_app(data_dir=None, sandbox=None, provider=None):
    load_local_config()
    app = FastAPI(title="Prooflane", version=__version__, docs_url=None, redoc_url=None, openapi_url=None)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        # Never echo credentials or malformed Unicode back in Pydantic error inputs.
        return JSONResponse({"detail": "Invalid input. Check field types, allowed sizes and UTF-8 text."}, status_code=422)

    store = Store(data_dir or os.getenv("PROOFLANE_DATA_DIR", str(ROOT / "data")))
    quarantine_file = store.path.parent / "sandbox-quarantine.json"
    quarantine = threading.Event()
    startup_checked = threading.Event()
    startup_lock = threading.Lock()
    if quarantine_file.exists():
        quarantine.set()
    sandbox = sandbox or DockerSandbox()
    provider = provider or VultrProvider()
    limiter = Limiter()
    slots = threading.BoundedSemaphore(2)
    origin = os.getenv("PROOFLANE_PUBLIC_ORIGIN", "http://127.0.0.1:8765").rstrip("/")
    hostname = urlsplit(origin).hostname
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list({"127.0.0.1", "localhost", "testserver", hostname or "127.0.0.1"}))

    @app.middleware("http")
    async def boundary(request: Request, call_next):
        if request.method == "POST":
            if request.headers.get("x-prooflane-request") != "1":
                return JSONResponse({"detail": "Missing same-origin request marker."}, status_code=403)
            if request.headers.get("origin") and request.headers["origin"] != origin:
                return JSONResponse({"detail": "Cross-origin requests are not allowed."}, status_code=403)
            if request.headers.get("content-type", "").split(";")[0] != "application/json":
                return JSONResponse({"detail": "Use application/json."}, status_code=415)
            body_limit = 8 * 1024 * 1024 if request.url.path == "/api/verify-packet" else (
                2 * 1024 * 1024 if request.url.path in {"/api/cases", "/api/cases/match"} else 180000)
            size, chunks = 0, []
            async for chunk in request.stream():
                size += len(chunk)
                if size > body_limit:
                    return JSONResponse({"detail": f"Request exceeds the {body_limit} byte limit for this operation."}, status_code=413)
                chunks.append(chunk)
            request._body = b"".join(chunks)
        session = request.cookies.get("prooflane_session", "")
        fresh = not re.fullmatch(r"[A-Za-z0-9_-]{43}", session)
        if fresh:
            session = secrets.token_urlsafe(32)
        request.state.owner = digest(session)
        response = await call_next(request)
        if fresh:
            response.set_cookie("prooflane_session", session, httponly=True, secure=origin.startswith("https://"),
                                samesite="strict", max_age=86400)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        response.headers["Cache-Control"] = "no-store"
        return response

    def live_enabled():
        return os.getenv("PROOFLANE_LIVE_ENABLED", "false").lower() == "true" and bool(os.getenv("PROOFLANE_OPERATOR_TOKEN"))

    def sandbox_health():
        if quarantine.is_set():
            return {"available": False, "detail": "Sandbox quarantined after unverified cleanup. Operator inspection is required."}
        if not startup_checked.is_set():
            with startup_lock:
                if not startup_checked.is_set():
                    try:
                        stale = sandbox.stale_containers() if hasattr(sandbox, "stale_containers") else []
                    except SandboxError as exc:
                        return {"available": False, "detail": str(exc)}
                    if stale:
                        quarantine.set()
                        quarantine_file.write_text(json.dumps({"reason":"startup_containers", "container_ids":stale[:100]}), encoding="utf-8")
                        return {"available": False, "detail": "Containers from an earlier service run need operator inspection. Execution is quarantined."}
                    startup_checked.set()
        return sandbox.available()

    def contain_failure(exc):
        if getattr(exc, "execution", {}).get("cleanup") is False:
            quarantine.set()
            quarantine_file.write_text(json.dumps({"reason": "cleanup_unverified", "at": datetime.now(timezone.utc).isoformat(),
                "container_id": exc.execution.get("container_id", "")}), encoding="utf-8")

    def acquire(request):
        address = request.client.host if request.client else "unknown"
        limiter.take("ip:" + address, 60)
        limiter.take("session:" + request.state.owner, 30)
        if not slots.acquire(blocking=False):
            raise HTTPException(429, "Two runs are already active. Try again shortly.")

    @app.get("/api/health")
    def health():
        return {"version": __version__, "docker": sandbox_health(),
                "inference": {"configured": provider.configured(), "enabled": live_enabled(), "model": provider.model}}

    @app.get("/api/sample")
    def sample():
        return {"csv": (ROOT / "examples" / "invoices.csv").read_text(encoding="utf-8"), "filename": "synthetic-invoices.csv"}

    @app.get("/api/runs")
    def list_runs(request: Request):
        return {"runs": [{**{key: run[key] for key in ("id", "status", "created_at", "mode", "filename")},
                          "total_variance": (run.get("summary") or {}).get("total_variance")} for run in store.list(request.state.owner)]}

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: str, request: Request):
        run = store.get(request.state.owner, run_id)
        if not run:
            raise HTTPException(404, "Run not found in this browser session.")
        return run

    @app.get("/api/runs/{run_id}/receipt")
    def receipt(run_id: str, request: Request):
        value = store.get(request.state.owner, run_id, receipt=True)
        if not value:
            raise HTTPException(404, "No verified receipt is available for this run.")
        return Response(json.dumps(value, indent=2), media_type="application/json",
                        headers={"Content-Disposition": f'attachment; filename="prooflane-{uuid.UUID(run_id)}.json"'})

    @app.post("/api/runs")
    def run_analysis(body: RunRequest, request: Request):
        return execute_run(body, request)

    def original_receipt(request, run_id):
        value = store.get(request.state.owner, run_id, receipt=True)
        if not value:
            raise HTTPException(404, "No verified baseline in this browser session.")
        if value.get("lineage") or value.get("case_context", {}).get("kind") == "alternative":
            raise HTTPException(422, "Choose the original review as baseline for another scenario.")
        return value

    @app.get("/api/runs/{run_id}/source")
    def scenario_source(run_id: str, request: Request):
        value = original_receipt(request, run_id)
        return {"baseline_run_id": run_id, "baseline_receipt_sha256": value["receipt_sha256"],
                "mode": value["provenance"]["mode"],
                "rows": [{k: row[k] for k in ("row", "invoice_id", "vendor", "quantity", "unit_price", "contract_price")}
                         for row in parse_csv(value["input_csv"])]}

    @app.post("/api/runs/{run_id}/scenario")
    def scenario(run_id: str, body: ScenarioRequest, request: Request):
        baseline = original_receipt(request, run_id)
        if body.baseline_receipt_sha256 != baseline["receipt_sha256"]:
            raise HTTPException(409, "Baseline receipt changed or does not match this review. Reopen the original review.")
        try:
            candidate, change = apply_assumption(baseline["input_csv"], body.row, body.field, body.value)
            run_request = RunRequest(csv=candidate, filename="hypothetical-scenario.csv",
                question="Recompute the fixed price comparison for a hypothetical change to one numeric source assumption.",
                mode=baseline["provenance"]["mode"], operator_token=body.operator_token)
        except InputError as exc:
            raise HTTPException(422, str(exc)[:300]) from exc
        except ValueError as exc:
            raise HTTPException(422, "Invalid scenario input.") from exc
        lineage = {"schema": "prooflane.scenario.v1", "baseline_run_id": run_id,
                   "baseline_receipt_sha256": baseline["receipt_sha256"], "change": change}
        return execute_run(run_request, request, baseline=baseline, lineage=lineage)

    @app.get("/api/runs/{run_id}/comparison")
    def comparison_packet(run_id: str, request: Request):
        scenario_receipt = store.get(request.state.owner, run_id, receipt=True)
        if not scenario_receipt or not scenario_receipt.get("lineage"):
            raise HTTPException(404, "No verified comparison in this browser session.")
        baseline = store.get(request.state.owner, scenario_receipt["lineage"]["baseline_run_id"], receipt=True)
        if not baseline:
            raise HTTPException(404, "The original review has expired. A previously downloaded packet can still be verified offline.")
        bundle = make_bundle(baseline, scenario_receipt)
        return Response(json.dumps(bundle, indent=2), media_type="application/json",
                        headers={"Content-Disposition": f'attachment; filename="prooflane-comparison-{uuid.UUID(run_id)}.json"'})

    def execute_run(body, request, baseline=None, lineage=None, case_context=None):
        try:
            rows = parse_csv(body.csv)
        except InputError as exc:
            raise HTTPException(422, str(exc)) from exc
        if body.mode == "vultr":
            if not live_enabled() or not provider.configured():
                raise HTTPException(503, "Live Vultr runs are disabled or not configured. Reference and sandbox modes remain available.")
            if not secrets.compare_digest(body.operator_token.encode("utf-8"), os.getenv("PROOFLANE_OPERATOR_TOKEN", "").encode("utf-8")):
                raise HTTPException(403, "An operator token is required for live inference.")
            limiter.take("live-global", 20, 86400)
            limiter.take("live:" + request.state.owner, 5)
        acquire(request)
        run = {"id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat(),
               "status": "failed", "mode": body.mode, "filename": body.filename,
               "question": body.question, "summary": None, "events": [], "code": "", "execution": {},
               "verification": {"passed": False, "checks": []}, "receipt_hash": "", "attempts": []}
        if lineage:
            run["lineage"] = lineage
        if case_context:
            run["case_context"] = case_context
        event = lambda stage, status, detail: run["events"].append({"stage": stage, "status": status, "detail": detail})
        receipt_value = None
        try:
            event("Validate", "passed", f"{len(rows)} records validated; USD; source records start at 2.")
            expected = summarize(rows)
            if body.mode == "reference":
                start = time.perf_counter()
                output = contract_output(expected)
                run["code"] = inspect.getsource(summarize)
                run["execution"] = {"runtime": "trusted-reference", "elapsed_ms": round((time.perf_counter()-start)*1000, 3)}
                event("Calculate", "passed", "Trusted reference arithmetic. No model call or sandbox execution.")
                run["verification"] = {"passed": True, "checks": [{"name": "Reference calculation", "passed": True,
                    "detail": "Fixed Decimal arithmetic; this mode is the baseline, not an independently verified agent run."}]}
            else:
                health = sandbox_health()
                if not health["available"]:
                    raise SandboxError(health["detail"] + " No code was executed.")
                repair_feedback = None
                for attempt in range(2 if body.mode == "vultr" else 1):
                    inference_evidence = {}
                    if body.mode == "vultr":
                        plan = provider.generate(body.question, len(rows), feedback=repair_feedback)
                        run["code"] = plan["code"]
                        run["model"] = plan["model"]
                        run["requested_model"] = plan["requested_model"]
                        inference_evidence = {"usage": plan.get("usage", {})}
                        if plan.get("request_id"):
                            inference_evidence["request_id"] = plan["request_id"]
                        event("Plan" if not attempt else "Repair", "passed", " | ".join(plan["plan"]))
                    else:
                        run["code"] = RECIPE
                        event("Plan", "passed", "Reviewed fixed recipe. No AI model call.")
                    try:
                        execution = sandbox.run(run["code"], body.csv)
                    except SandboxError as exc:
                        # Only a confirmed-clean execution failure permits one repair.
                        # Never retry uncertain cleanup or control-plane availability failures.
                        if body.mode == "vultr" and attempt == 0 and exc.execution.get("cleanup") is True:
                            run["execution"] = exc.execution
                            run["attempts"].append({"index": attempt + 1, "code": run["code"],
                                "execution": exc.execution, "error": str(exc)[:600], "model": run.get("model"),
                                **inference_evidence})
                            event("Execute", "failed", "Execution failed; cleanup confirmed. One bounded repair is allowed.")
                            repair_feedback = "Previous execution exceeded a runtime limit or failed. Cleanup was confirmed. Return a simpler complete program within the fixed resource and arithmetic contract."
                            continue
                        raise
                    run["execution"] = {**execution, "runtime": "docker"}
                    event("Execute", "passed" if execution["exit_code"] == 0 else "failed",
                          f"Disposable Docker execution; exit={execution['exit_code']}; cleanup={execution['cleanup']}.")
                    try:
                        output = json.loads(execution["stdout"], parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-finite")))
                    except (ValueError, TypeError, RecursionError):
                        output = None
                    verification = verify_output(output, expected)
                    if execution["exit_code"] != 0 or not execution["cleanup"]:
                        verification["passed"] = False
                        verification["checks"].append({"name": "Execution and cleanup", "passed": False, "detail": "Nonzero exit or cleanup not confirmed."})
                    run["verification"] = verification
                    run["attempts"].append({"index": attempt + 1, "code": run["code"], "execution": execution,
                        "verification": verification, "model": run.get("model"),
                        "usage": {}, **inference_evidence})
                    event("Verify", "passed" if verification["passed"] else "failed", "Independent verifier checked totals and every finding.")
                    if verification["passed"]:
                        break
                    failed_checks = [check["name"] for check in verification["checks"] if not check["passed"]]
                    repair_feedback = "Previous program failed these fixed checks: " + ", ".join(failed_checks) + ". Regenerate a complete compliant program; never change the arithmetic contract."
                if not run["verification"]["passed"]:
                    raise ValueError("Result failed independent checks. Unverified figures have been withheld.")
            run["status"] = "verified"
            run["summary"] = expected
            run["explanation"] = (f"{expected['flagged_count']} of {expected['row_count']} records have a positive price difference, "
                                  f"totalling USD {expected['total_variance']}. Review the cited records against the contract. "
                                  "This is a price comparison, not proof of an incorrect invoice or recoverable savings.")
            if body.mode == "vultr":
                try:
                    explanation = provider.explain(expected["row_count"], expected["flagged_count"])
                    scope = f"{expected['flagged_count']} of {expected['row_count']} included records have a positive price difference."
                    variance = f"Positive price differences total USD {expected['total_variance']}."
                    lead = [variance, scope] if explanation["lead"] == "variance" else [scope, variance]
                    next_step = ("Review the cited invoice and contract rows together." if explanation["review"] == "contracts"
                                 else "Review the included records and confirm the scope is complete.")
                    run["explanation"] = " ".join([*lead, next_step])
                    run["explanation_trace"] = {"status": "checked", **explanation}
                    event("Explain", "passed", "Vultr chose the explanation focus and review step. Values came from the independently checked result.")
                except ProviderError:
                    run["explanation_trace"] = {"status": "unavailable"}
                    event("Explain", "skipped", "Vultr explanation unavailable. Showing the checked application summary.")
            event("Receipt", "passed", "Input, code and output bound by SHA-256. Integrity only; no issuer authentication.")
            receipt_value = make_receipt({"run_id": run["id"], "created_at": run["created_at"],
                "input_csv": body.csv, "code": run["code"], "output": output, "summary": expected,
                "verification": run["verification"], "events": run["events"], "execution": run["execution"], "attempts": run["attempts"],
                "provenance": {"mode": body.mode, "model": run.get("model"), "requested_model": run.get("requested_model"),
                               "model_calls": (attempt+2) if body.mode == "vultr" else 0,
                               "raw_records_sent_to_model": False}, "question": body.question,
                **({"explanation_trace": run["explanation_trace"], "explanation": run["explanation"]} if body.mode == "vultr" else {}),
                               **({"lineage": lineage} if lineage else {}),
                               **({"case_context": case_context} if case_context else {})})
            run["receipt_hash"] = receipt_value["receipt_sha256"]
            if lineage:
                run["comparison"] = compare_receipts(baseline, receipt_value)
        except (SandboxError, ProviderError, ValueError) as exc:
            run["status"] = "failed"
            run["summary"] = None
            run["receipt_hash"] = ""
            receipt_value = None
            run["error"] = str(exc)[:600]
            event("Stopped", "failed", run["error"])
            if isinstance(exc, SandboxError) and getattr(exc, "execution", None):
                run["execution"] = exc.execution
                run["attempts"].append({"index":len(run["attempts"])+1, "code":run["code"],
                    "execution":exc.execution, "error":run["error"], "model":run.get("model")})
                contain_failure(exc)
        finally:
            slots.release()
        try:
            store.add(request.state.owner, run, receipt_value)
        except RuntimeError as exc:
            raise HTTPException(503, str(exc)) from exc
        return run

    @app.post("/api/containment")
    def containment(request: Request):
        acquire(request)
        try:
            health = sandbox_health()
            if not health["available"]:
                raise SandboxError(health["detail"])
            return sandbox.probe()
        except SandboxError as exc:
            contain_failure(exc)
            raise HTTPException(503, str(exc)[:600]) from exc
        finally:
            slots.release()

    register_case_routes(app, store, execute_run, RunRequest, limiter)

    @app.get("/")
    def index():
        return FileResponse(ROOT / "web" / "index.html")

    app.mount("/static", StaticFiles(directory=ROOT / "web", check_dir=False), name="static")
    return app


app = create_app()
