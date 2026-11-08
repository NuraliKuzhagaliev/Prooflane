"""Session-owned decision workbench; all executable alternatives use the existing runner."""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .analysis import InputError, canonical, digest
from .case_evidence import check_case_packet, make_case_packet
from .case_store import CaseStore, StaleCase
from .comparison import check_bundle
from .intelligence import apply_changes, comparison_delta, explore, targets_for, validated_bounds
from .receipts import check_receipt
from .priority import priority_switch
from .operations import CaseLocks, OperationConflict, OperationStore
from .strict_json import load_evidence_json
from .reconciliation import reconcile, source_result
from .review_insights import handoff_csv, review_brief, review_insights


class CaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("name", "operator_token", check_fields=False)
    @classmethod
    def valid_text(cls, value):
        value.encode("utf-8")
        return value


class MatchRequest(CaseModel):
    invoices_csv: str = Field(min_length=1, max_length=131072)
    contracts_csv: str = Field(min_length=1, max_length=131072)
    selections: dict[str, str] = Field(default_factory=dict)
    exclusions: dict[str, str] = Field(default_factory=dict)


class CreateCaseRequest(CaseModel):
    request_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    name: str = Field(min_length=1, max_length=80)
    baseline_run_id: str | None = Field(default=None, max_length=64)
    mode: str = Field(default="reference", pattern="^(reference|sandbox|vultr)$")
    operator_token: str = Field(default="", max_length=256)
    invoices_csv: str | None = Field(default=None, min_length=1, max_length=131072)
    contracts_csv: str | None = Field(default=None, min_length=1, max_length=131072)
    selections: dict[str, str] = Field(default_factory=dict)
    exclusions: dict[str, str] = Field(default_factory=dict)


class VariantRequest(CaseModel):
    request_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    revision: int = Field(strict=True, ge=1)
    name: str = Field(min_length=1, max_length=80)
    changes: list[dict] = Field(min_length=1, max_length=12)
    operator_token: str = Field(default="", max_length=256)


class BoundsRequest(CaseModel):
    revision: int = Field(strict=True, ge=1)
    bounds: list[dict] = Field(max_length=24)


def register_case_routes(app, store, execute_run, run_model, limiter):
    cases = CaseStore(store)
    operations = OperationStore(store, cases)
    # Unrelated cases may progress independently; global run slots still cap execution.
    mutation_locks = CaseLocks()

    def quota(request):
        address = request.client.host if request.client else "unknown"
        limiter.take("case-ip:" + address, 240)
        limiter.take("case-session:" + request.state.owner, 120)

    def load(request, case_id):
        case = cases.get(request.state.owner, case_id)
        if not case:
            raise HTTPException(404, "Case not found in this browser session, or it expired.")
        return case

    def run_value(request, run_id, receipt=False):
        value = store.get(request.state.owner, run_id, receipt=receipt)
        if not value:
            raise HTTPException(404, "A source run has expired. Previously downloaded packets remain verifiable offline.")
        return value

    def original(request, run_id):
        value = run_value(request, run_id, receipt=True)
        if value.get("lineage") or value.get("case_context", {}).get("kind") == "alternative":
            raise HTTPException(422, "A new case needs an original verified review, not an alternative.")
        check_receipt(value)
        return value

    def render(request, case):
        source = source_result(case["sources"])
        targets = targets_for(source["canonical_csv"], source["bindings"])
        baseline = run_value(request, case["baseline_run_id"])
        variants = []
        for v in case["variants"]:
            run = run_value(request, v["run_id"])
            variants.append({"id": v["run_id"], "name": v["name"], "changes": v["changes"],
                             "changed_rows": v["changed_rows"], "run": run,
                             "delta": comparison_delta(baseline["summary"], run["summary"])})
        return {**{k: case[k] for k in ("id", "name", "created_at", "revision", "bounds")},
                "baseline": baseline, "source": {"kind": case["sources"]["kind"], **{k: v for k, v in source.items() if k != "canonical_csv"}},
                "targets": targets, "intelligence": explore(source["canonical_csv"], targets, case["bounds"]),
                "priority_switch": priority_switch(source["canonical_csv"], targets),
                "review_insights": review_insights(source),
                "variants": variants, "limits": {"max_variants": 4, "max_changes": 12, "max_bounds": 24}}

    def acquire_case(case, revision):
        if case["revision"] != revision:
            raise HTTPException(409, "The case changed. Reopen it before applying another change.")

    def replay_operation(request, operation):
        if operation["status"] == "pending":
            return JSONResponse({"operation": operation}, status_code=202, headers={"Retry-After": "2"})
        if operation["status"] == "interrupted":
            return JSONResponse({"detail": operation["error"], "operation": operation}, status_code=409)
        result = {"operation": operation}
        if operation.get("case_id"):
            result["case"] = render(request, load(request, operation["case_id"]))
        if operation.get("failed_run_id"):
            result["failed_run"] = run_value(request, operation["failed_run_id"])
        status = operation["http_status"]
        if status >= 400:
            result["detail"] = operation.get("error") or "The original request failed. Inspect the recorded result before starting another operation."
        return JSONResponse(result, status_code=status)

    def execute_operation(request, body, scope, case_id, action):
        operation = None
        if body.request_id:
            payload = body.model_dump(exclude={"operator_token", "request_id"})
            try:
                # Field presence affects the accepted create contract (e.g. a
                # promoted baseline may not include an explicit execution mode).
                fingerprint = digest(canonical({'payload': payload, 'fields': sorted(body.model_fields_set - {'operator_token', 'request_id'})}))
            except (ValueError, TypeError, RecursionError) as exc:
                raise HTTPException(422, "Invalid input. Check field types and UTF-8 text.") from exc
            try:
                operation, reserved = operations.begin(request.state.owner, body.request_id, scope,
                                                       fingerprint, case_id)
            except OperationConflict as exc:
                raise HTTPException(409, str(exc)) from exc
            if not reserved:
                return replay_operation(request, operation)
        try:
            result = action()
        except HTTPException as exc:
            if not operation:
                raise
            operation = operations.finish(request.state.owner, body.request_id, "failed", case_id=None,
                http_status=exc.status_code, error=f"The original request failed (HTTP {exc.status_code}). Check inputs or configuration before starting a new request.")
            return JSONResponse({"detail": exc.detail, "operation": operation}, status_code=exc.status_code)
        except Exception:
            if operation:
                operations.finish(request.state.owner, body.request_id, "interrupted", case_id=case_id,
                    http_status=409, error="Completion could not be confirmed. This request will not execute again. Inspect the archive before starting another request.")
            raise
        if not operation:
            return result
        status = result.status_code if isinstance(result, JSONResponse) else 200
        value = json.loads(result.body) if isinstance(result, JSONResponse) else result
        failed = value.get("failed_run")
        operation = operations.finish(request.state.owner, body.request_id, "failed" if failed else "completed",
            case_id=value.get("case", {}).get("id"), failed_run_id=failed["id"] if failed else None,
            http_status=status, error="The recorded execution failed. Inspect its diagnostics before starting a new request." if failed else None)
        return JSONResponse({**value, "operation": operation}, status_code=status)

    @app.get("/api/operations/{operation_id}")
    def operation_status(operation_id: str, request: Request):
        quota(request)
        operation = operations.get(request.state.owner, operation_id)
        if not operation:
            raise HTTPException(404, "Operation not found in this browser session, or it expired.")
        return {"operation": operation}

    @app.get("/api/cases/sample")
    def sample():
        root = Path(__file__).resolve().parents[1] / "examples"
        return {"name": "November supplier review · synthetic", "invoices_csv": (root / "case-invoices.csv").read_text(encoding="utf-8"),
                "contracts_csv": (root / "case-contracts.csv").read_text(encoding="utf-8")}

    @app.post("/api/cases/match")
    def match(body: MatchRequest, request: Request):
        quota(request)
        try:
            source = reconcile(body.invoices_csv, body.contracts_csv, body.selections, body.exclusions)
            return {**source, "review_insights": review_insights(source)}
        except InputError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/api/cases")
    def list_cases(request: Request):
        return {"cases": [{**{k: c[k] for k in ("id", "name", "created_at", "baseline_run_id", "mode", "revision")},
                            "variant_count": len(c["variants"])} for c in cases.list(request.state.owner)
                           if store.get(request.state.owner, c["baseline_run_id"])]}

    @app.post("/api/cases")
    def create(body: CreateCaseRequest, request: Request):
        quota(request)
        case_id = str(uuid.uuid4())
        return execute_operation(request, body, "create", case_id, lambda: create_work(body, request, case_id))

    def create_work(body, request, case_id):
        if not body.name.strip():
            raise HTTPException(422, "Give the case a name.")
        try:
            if body.baseline_run_id:
                if body.model_fields_set - {"name", "baseline_run_id", "request_id"}:
                    raise InputError("Choose either an existing original review or two source files, without mixing modes or inputs.")
                receipt = original(request, body.baseline_run_id)
                sources = {"kind": "embedded", "csv": receipt["input_csv"]}
                baseline_id, mode = receipt["run_id"], receipt["provenance"]["mode"]
            else:
                sources = {"kind": "contracts", "invoices_csv": body.invoices_csv, "contracts_csv": body.contracts_csv,
                           "selections": body.selections, "exclusions": body.exclusions}
                source = source_result(sources)
                run = execute_run(run_model(csv=source["canonical_csv"], filename="reconciled-invoices.csv", mode=body.mode,
                    question="Compare invoice prices with the explicitly resolved dated contract sources.", operator_token=body.operator_token),
                    request, case_context={"kind": "baseline", "case_id": case_id})
                if run["status"] != "verified":
                    return JSONResponse({"detail": "Baseline execution failed; no case was created.", "failed_run": run}, status_code=422)
                baseline_id, mode = run["id"], body.mode
            case = {"id": case_id, "name": body.name.strip(), "created_at": datetime.now(timezone.utc).isoformat(), "revision": 1,
                    "sources": sources, "baseline_run_id": baseline_id, "mode": mode, "bounds": [], "variants": []}
            cases.add(request.state.owner, case)
            return {"case": render(request, case)}
        except (InputError, ValueError) as exc:
            raise HTTPException(422, str(exc)[:300]) from exc

    @app.get("/api/cases/{case_id}")
    def get_case(case_id: str, request: Request):
        quota(request)
        return {"case": render(request, load(request, case_id))}

    @app.post("/api/cases/{case_id}/variants")
    def variant(case_id: str, body: VariantRequest, request: Request):
        quota(request)
        return execute_operation(request, body, "variant:" + case_id, case_id, lambda: variant_work(case_id, body, request))

    def variant_work(case_id, body, request):
        load(request, case_id)
        if not mutation_locks.acquire(request.state.owner, case_id):
            raise HTTPException(409, "Another update of this case is running. Reopen it when the update finishes.")
        try:
            case = load(request, case_id)
            acquire_case(case, body.revision)
            name = body.name.strip()
            if not name or any(v["name"] == name for v in case["variants"]):
                raise InputError("Give each alternative a distinct name.")
            if len(case["variants"]) >= 4:
                raise InputError("A case supports at most four executed alternatives.")
            baseline = original(request, case["baseline_run_id"])
            source = source_result(case["sources"])
            targets = targets_for(source["canonical_csv"], source["bindings"])
            candidate, changes, rows = apply_changes(source["canonical_csv"], targets, body.changes)
            context = {"kind": "alternative", "case_id": case_id, "baseline_run_id": baseline["run_id"],
                       "baseline_receipt_sha256": baseline["receipt_sha256"], "changes": changes}
            run = execute_run(run_model(csv=candidate, filename="case-alternative.csv", mode=baseline["provenance"]["mode"],
                question="Jointly recompute the declared hypothetical assumptions against the original baseline.",
                operator_token=body.operator_token), request, case_context=context)
            if run["status"] != "verified":
                return {"case": render(request, case), "failed_run": run}
            case["variants"].append({"name": name, "run_id": run["id"], "changes": changes, "changed_rows": rows,
                                     **({"request_id": body.request_id} if body.request_id else {})})
            case = cases.update(request.state.owner, case, body.revision)
            return {"case": render(request, case)}
        except StaleCase as exc:
            raise HTTPException(409, str(exc)) from exc
        except (InputError, ValueError) as exc:
            raise HTTPException(422, str(exc)[:300]) from exc
        finally:
            mutation_locks.release(request.state.owner, case_id)

    @app.post("/api/cases/{case_id}/bounds")
    def bounds(case_id: str, body: BoundsRequest, request: Request):
        quota(request)
        load(request, case_id)
        if not mutation_locks.acquire(request.state.owner, case_id):
            raise HTTPException(409, "Another update of this case is running. Reopen it when the update finishes.")
        try:
            case = load(request, case_id)
            acquire_case(case, body.revision)
            run_value(request, case["baseline_run_id"], receipt=True)
            source = source_result(case["sources"])
            targets = targets_for(source["canonical_csv"], source["bindings"])
            case["bounds"] = validated_bounds(targets, body.bounds)
            # Complete the computation before publishing a revision.
            explore(source["canonical_csv"], targets, case["bounds"])
            case = cases.update(request.state.owner, case, body.revision)
            return {"case": render(request, case)}
        except StaleCase as exc:
            raise HTTPException(409, str(exc)) from exc
        except (InputError, ValueError) as exc:
            raise HTTPException(422, str(exc)[:300]) from exc
        finally:
            mutation_locks.release(request.state.owner, case_id)

    @app.get("/api/cases/{case_id}/packet")
    def packet(case_id: str, request: Request):
        quota(request)
        case = load(request, case_id)
        baseline = run_value(request, case["baseline_run_id"], receipt=True)
        alternatives = [{"name": v["name"], "changes": v["changes"], "changed_rows": v["changed_rows"],
                         "receipt": run_value(request, v["run_id"], receipt=True)} for v in case["variants"]]
        try:
            value = make_case_packet(case, baseline, alternatives)
        except ValueError as exc:
            raise HTTPException(422, str(exc)[:300]) from exc
        return Response(canonical(value), media_type="application/json",
                        headers={"Content-Disposition": f'attachment; filename="prooflane-case-{uuid.UUID(case_id)}.json"'})

    @app.get("/api/cases/{case_id}/handoff.csv")
    def handoff(case_id: str, request: Request):
        quota(request)
        case = load(request, case_id)
        run_value(request, case['baseline_run_id'])
        return Response(handoff_csv(source_result(case['sources'])), media_type='text/csv',
                        headers={'Content-Disposition': f'attachment; filename="prooflane-rows-{uuid.UUID(case_id)}.csv"'})

    @app.get("/api/cases/{case_id}/brief.md")
    def brief(case_id: str, request: Request):
        quota(request)
        case = load(request, case_id)
        return Response(review_brief(render(request, case)), media_type='text/markdown',
                        headers={'Content-Disposition': f'attachment; filename="prooflane-brief-{uuid.UUID(case_id)}.md"'})

    @app.post("/api/verify-packet")
    async def verify_packet(request: Request):
        quota(request)
        try:
            artifact = load_evidence_json(await request.body())
            schema = artifact.get("schema") if isinstance(artifact, dict) else None
            checker = check_case_packet if schema == "prooflane.case.v1" else check_bundle if schema == "prooflane.comparison.v1" else check_receipt
            result = checker(artifact)
            return {"passed": True, **result}
        except (ValueError, KeyError, TypeError, RecursionError, AttributeError, OverflowError):
            return {"passed": False, "error": "Packet verification failed: invalid structure, source reconciliation, assumptions, arithmetic or hash. No code was executed."}
