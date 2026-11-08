"""Independent local API/linkage probes. No real provider or Docker calls."""
from pathlib import Path

# Repeat the exact original orchestration probes, preserving original evidence.
original = Path(__file__).with_name("engineering_probe.py").read_text(encoding="utf-8")
original = original.replace('"probe-data-"', '"cycle1-data-"')
original = original.replace('"engineering-probes.json"', '"engineering-cycle1-retests.json"')
exec(compile(original, str(Path(__file__)), "exec"), globals())

import copy
import hashlib
import sqlite3
from prooflane.analysis import canonical, digest
from prooflane.comparison import apply_assumption, check_bundle, make_bundle
from prooflane.receipts import make_receipt

checks = []
def capture(name, callback):
    try:
        value = callback()
        checks.append({"case":name, "result":value})
    except Exception as exc:
        checks.append({"case":name, "exception":type(exc).__name__, "error":str(exc)[:300]})

def receipt_for(text, ident, lineage=None, mode="reference"):
    summary = summarize(parse_csv(text))
    return make_receipt({"run_id":ident,"input_csv":text,"code":"review only",
        "summary":summary,"output":contract_output(summary),"provenance":{"mode":mode,"model_calls":0},
        **({"lineage":lineage} if lineage else {})})

SOURCE = "invoice_id,vendor,quantity,unit_price,contract_price,notes\nA,North,2,10,8,first\nB,South,3,6,8,second\n"
base = receipt_for(SOURCE, "baseline")
changed, change = apply_assumption(SOURCE, 2, "contract_price", "9")
lineage = {"schema":"prooflane.scenario.v1","baseline_run_id":"baseline",
    "baseline_receipt_sha256":base["receipt_sha256"],"change":change}
candidate = receipt_for(changed, "scenario", lineage)
bundle = make_bundle(base, candidate)
capture("valid_bundle", lambda: check_bundle(bundle)["comparison"]["delta"])
for name, altered in {
    "hidden_notes_edit":changed.replace("second", "undeclared"),
    "hidden_other_price_edit":changed.replace("B,South,3,6,8", "B,South,3,7,8"),
    "hidden_same_row_vendor_edit":changed.replace("A,North", "A,Elsewhere"),
    "hidden_numeric_equivalence_edit":changed.replace("B,South,3,6,8", "B,South,3,6.0,8"),
    "removed_record":changed.splitlines()[0]+"\n"+changed.splitlines()[1]+"\n",
}.items():
    forged = receipt_for(altered, "scenario", copy.deepcopy(lineage))
    capture(name, lambda forged=forged: make_bundle(base, forged))

for name, mutate in {
    "parent_substitution":lambda b: b["scenario"]["lineage"].update(baseline_receipt_sha256="f"*64),
    "false_original_value":lambda b: b["scenario"]["lineage"]["change"].update(before="7"),
    "mode_mismatch":lambda b: b["scenario"]["provenance"].update(mode="sandbox"),
    "delta_forgery":lambda b: b["comparison"]["delta"].update(total_variance="-99.00"),
}.items():
    forged = copy.deepcopy(bundle)
    mutate(forged)
    forged["scenario"] = make_receipt(forged["scenario"])
    # make_receipt expects payload without an old receipt hash.
    forged["scenario"].pop("receipt_sha256")
    forged["scenario"] = make_receipt(forged["scenario"])
    forged["bundle_sha256"] = digest(canonical({k:v for k,v in forged.items() if k != "bundle_sha256"}))
    capture(name, lambda forged=forged:check_bundle(forged))

for name, plan, returned_model in (
    ("surrogate_plan", ["\ud800"], "review-only"),
    ("surrogate_model", ["calculate"], "\ud800"),
):
    plan_payload = {"plan":plan, "code":"# review only; never executed"}
    envelope = {"model":returned_model,"choices":[{"finish_reason":"stop", "message":{"content":json.dumps(plan_payload)}}]}
    def respond(request, envelope=envelope):
        return httpx.Response(200, content=json.dumps(envelope).encode("ascii"), headers={"Content-Type":"application/json"})
    provider = VultrProvider.__new__(VultrProvider)
    provider.key = "review-only-not-real"
    provider.model = "review-only"
    sandbox = FakeSandbox("normal")
    app = app_module.create_app(SESSION / name, provider=provider, sandbox=sandbox)
    with patch.object(httpx, "Client", lambda **kw: original_client(transport=httpx.MockTransport(respond), **kw)):
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post("/api/runs", json=PAYLOAD, headers=HEADERS)
            stored = client.get("/api/runs").json()["runs"]
    with sqlite3.connect(SESSION / name / "prooflane.sqlite3") as connection:
        database_statuses = [json.loads(row[0])["status"] for row in connection.execute("select run from runs")]
    checks.append({"case":name,"http_status":response.status_code,"sandbox_calls":sandbox.calls,
                   "stored_statuses":[r["status"] for r in stored],"database_statuses":database_statuses})

class StatefulSandbox:
    behavior = "good"
    calls = 0
    def available(self): return {"available":True,"detail":"Audit double"}
    def stale_containers(self): return []
    def run(self, code, csv):
        self.calls += 1
        if self.behavior == "uncertain":
            raise SandboxError("Uncertain cleanup", {"cleanup":False,"container_id":"review-double"})
        if self.behavior == "unknown":
            raise SandboxError("Unknown execution state")
        return {"stdout":json.dumps(contract_output(summarize(parse_csv(csv)))),
                "stderr":"","exit_code":0,"cleanup":True,"elapsed_ms":1}

for cleanup_case in ("uncertain", "unknown"):
    sandbox, provider = StatefulSandbox(), FakeProvider()
    app = app_module.create_app(SESSION / cleanup_case, provider=provider, sandbox=sandbox)
    with TestClient(app, raise_server_exceptions=False) as client, TestClient(app, raise_server_exceptions=False) as stranger:
        baseline = client.post("/api/runs", json=PAYLOAD, headers=HEADERS).json()
        baseline_bytes = client.get(f"/api/runs/{baseline['id']}").content
        payload = {"baseline_receipt_sha256":baseline["receipt_hash"], "row":2,
                   "field":"contract_price", "value":"1.5", "operator_token":"review-only-not-a-secret"}
        endpoint = f"/api/runs/{baseline['id']}/scenario"
        missing_token = client.post(endpoint, json={**payload,"operator_token":""}, headers=HEADERS).status_code
        foreign = stranger.post(endpoint, json=payload, headers=HEADERS).status_code
        sandbox.behavior = cleanup_case
        calls_before = sandbox.calls
        response = client.post(endpoint, json=payload, headers=HEADERS)
        scenario = response.json()
        receipt_status = client.get(f"/api/runs/{scenario['id']}/comparison").status_code
        unchanged = baseline_bytes == client.get(f"/api/runs/{baseline['id']}").content
        checks.append({"case":"scenario_"+cleanup_case, "http_status":response.status_code,
            "status":scenario["status"],"sandbox_calls":sandbox.calls-calls_before,"export_status":receipt_status,
            "baseline_unchanged":unchanged,"foreign_status":foreign,"missing_live_token_status":missing_token})

fingerprints = {path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in
    ("prooflane/app.py","prooflane/provider.py","prooflane/comparison.py","scripts/verify_receipt.py")}
(OUT / "engineering-cycle1-probes.json").write_text(json.dumps({"scope":"MOCKED_API_AND_LOCAL_VERIFIER_NOT_LIVE",
    "file_sha256":fingerprints,"checks":checks},indent=2),encoding="utf-8")
print(json.dumps(checks, ensure_ascii=True, indent=2))
