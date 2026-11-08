"""Frozen-source independent cycle 2. Local doubles and offline artifacts only."""
from pathlib import Path

header = Path(__file__).with_name("engineering_probe.py").read_text(encoding="utf-8").split("results = []")[0]
header = header.replace('"probe-data-"', '"cycle2-data-"')
exec(compile(header, str(Path(__file__)), "exec"), globals())

import copy
import hashlib
import subprocess
from prooflane.analysis import canonical, digest
from prooflane.receipts import check_receipt, make_receipt

records = []

def record(case, **result):
    records.append({"case":case, **result})

provider, sandbox = FakeProvider(), FakeSandbox("timeout_then_success")
with TestClient(app_module.create_app(SESSION / "E1", provider=provider, sandbox=sandbox)) as client:
    run = client.post("/api/runs", json=PAYLOAD, headers=HEADERS).json()
    record("E1_clean_timeout", passed=run["status"]=="verified" and len(run["attempts"])==2,
           status=run["status"], provider_calls=provider.calls, sandbox_calls=sandbox.calls)

original_client = httpx.Client
for name, envelope in (
    ("E2_null_choice", {"choices":[None]}),
    ("E3_plan_surrogate", {"model":"fixture", "choices":[{"finish_reason":"stop","message":{
        "content":json.dumps({"plan":["\ud800"],"code":"pass"})}}]}),
    ("E3_model_surrogate", {"model":"\ud800", "choices":[{"finish_reason":"stop","message":{
        "content":json.dumps({"plan":["calculate"],"code":"pass"})}}]}),
):
    provider = VultrProvider.__new__(VultrProvider)
    provider.key, provider.model = "fixture-not-secret", "fixture"
    sandbox = FakeSandbox("normal")
    def respond(request, envelope=envelope):
        return httpx.Response(200, content=json.dumps(envelope).encode("ascii"))
    with patch.object(httpx,"Client",lambda **kw: original_client(transport=httpx.MockTransport(respond), **kw)):
        with TestClient(app_module.create_app(SESSION/name, provider=provider, sandbox=sandbox), raise_server_exceptions=False) as client:
            response = client.post("/api/runs",json=PAYLOAD,headers=HEADERS)
            run = response.json()
            history = client.get("/api/runs").json()["runs"]
            record(name, passed=response.status_code==200 and run["status"]=="failed" and sandbox.calls==0 and len(history)==1,
                   http_status=response.status_code,status=run["status"],sandbox_calls=sandbox.calls,history_count=len(history))

class OfflineSandbox:
    calls = 0
    def stale_containers(self): return []
    def available(self): return {"available":False,"detail":"Reviewer simulated Docker absence"}
    def run(self,*args):
        self.calls += 1
        raise AssertionError("No runtime execution permitted")

provider, sandbox = FakeProvider(), OfflineSandbox()
with TestClient(app_module.create_app(SESSION/"offline",provider=provider,sandbox=sandbox)) as client:
    for mode in ("sandbox","vultr"):
        run = client.post("/api/runs",json={**PAYLOAD,"mode":mode},headers=HEADERS).json()
        record("no_docker_"+mode,passed=run["status"]=="failed" and run["summary"] is None and not run["receipt_hash"] and sandbox.calls==0 and provider.calls==0,
               status=run["status"],sandbox_calls=sandbox.calls,provider_calls=provider.calls)

with TestClient(app_module.create_app(SESSION/"scenario",sandbox=OfflineSandbox())) as owner:
    app = owner.app
    baseline = owner.post("/api/runs",json={"csv":CSV,"mode":"reference"},headers=HEADERS).json()
    before = owner.get(f"/api/runs/{baseline['id']}").content
    endpoint = f"/api/runs/{baseline['id']}/scenario"
    payload = {"baseline_receipt_sha256":baseline["receipt_hash"],"row":2,"field":"quantity","value":"3"}
    response = owner.post(endpoint,json=payload,headers=HEADERS)
    scenario = response.json()
    record("scenario_signed_exact_delta",passed=scenario["status"]=="verified" and scenario["comparison"]["delta"]=={
        "total_variance":"2.00","total_billed":"4.00","flagged_count":0},delta=scenario["comparison"]["delta"])
    record("baseline_immutable",passed=owner.get(f"/api/runs/{baseline['id']}").content==before)
    statuses = {
        "wrong_hash":owner.post(endpoint,json={**payload,"baseline_receipt_sha256":"f"*64},headers=HEADERS).status_code,
        "mode_override":owner.post(endpoint,json={**payload,"mode":"vultr"},headers=HEADERS).status_code,
        "missing_csrf":owner.post(endpoint,json=payload).status_code,
        "scenario_as_parent":owner.post(f"/api/runs/{scenario['id']}/scenario",json={**payload,"baseline_receipt_sha256":scenario['receipt_hash']},headers=HEADERS).status_code,
    }
    with TestClient(app) as stranger:
        statuses["foreign_source"] = stranger.get(f"/api/runs/{baseline['id']}/source").status_code
        statuses["foreign_scenario"] = stranger.post(endpoint,json=payload,headers=HEADERS).status_code
        statuses["foreign_comparison"] = stranger.get(f"/api/runs/{scenario['id']}/comparison").status_code
    record("lineage_and_access_boundaries",passed=statuses=={"wrong_hash":409,"mode_override":422,"missing_csrf":403,
        "scenario_as_parent":422,"foreign_source":404,"foreign_scenario":404,"foreign_comparison":404},statuses=statuses)

    # Corrupt only the synthetic executor status on a new app: no real Docker or data touched.
    packet = owner.get(f"/api/runs/{scenario['id']}/comparison").json()
    original_packet = OUT / "cycle2-original-packet.json"
    original_packet.write_text(json.dumps(packet),encoding="utf-8")

for name, artifact in (("real_reference",ROOT/"artifacts/optimization/reference-comparison.json"),
                       ("real_docker",ROOT/"artifacts/optimization/sandbox-comparison.json"),
                       ("fresh_reference",original_packet)):
    result = subprocess.run([sys.executable,str(ROOT/"scripts/verify_receipt.py"),str(artifact)],
                            capture_output=True,text=True,timeout=15)
    record("offline_CLI_"+name,passed=result.returncode==0,exit_code=result.returncode,
           output=json.loads(result.stdout) if result.returncode==0 else result.stderr[:500])

for kind in ("hidden_notes", "hidden_numeric", "false_delta"):
    forged = copy.deepcopy(packet)
    if kind != "false_delta":
        scenario_payload = {k:v for k,v in forged["scenario"].items() if k != "receipt_sha256"}
        if kind == "hidden_notes":
            scenario_payload["input_csv"] = scenario_payload["input_csv"].replace("Synthetic", "Undeclared")
        else:
            scenario_payload["input_csv"] = scenario_payload["input_csv"].replace(",3,2,1,",",3,4,1,")
        summary = summarize(parse_csv(scenario_payload["input_csv"]))
        scenario_payload["summary"], scenario_payload["output"] = summary, contract_output(summary)
        forged["scenario"] = make_receipt(scenario_payload)
    else:
        forged["comparison"]["delta"]["total_variance"] = "-900.00"
    individual_valid = check_receipt(forged["baseline"])["passed"] and check_receipt(forged["scenario"])["passed"]
    forged["bundle_sha256"] = digest(canonical({k:v for k,v in forged.items() if k != "bundle_sha256"}))
    path = OUT / ("cycle2-forged-"+kind+".json")
    path.write_text(json.dumps(forged),encoding="utf-8")
    result = subprocess.run([sys.executable,str(ROOT/"scripts/verify_receipt.py"),str(path)],capture_output=True,text=True,timeout=15)
    record("offline_CLI_rehashed_"+kind,passed=individual_valid and result.returncode!=0,
           individual_receipts_valid=individual_valid,exit_code=result.returncode,error=result.stderr.strip())

class ScenarioFailureSandbox(FakeSandbox):
    failing = False
    def run(self, *args):
        if self.failing:
            self.calls += 1
            raise SandboxError("Reviewer synthetic cleanup failure", {"cleanup":False,"container_id":"cycle2-fixture"})
        return super().run(*args)

provider, sandbox = FakeProvider(), ScenarioFailureSandbox("normal")
with TestClient(app_module.create_app(SESSION/"failed-scenario",provider=provider,sandbox=sandbox)) as client:
    baseline = client.post("/api/runs",json=PAYLOAD,headers=HEADERS).json()
    before = client.get(f"/api/runs/{baseline['id']}").content
    endpoint = f"/api/runs/{baseline['id']}/scenario"
    payload = {"baseline_receipt_sha256":baseline["receipt_hash"],"row":2,"field":"quantity","value":"3"}
    auth_status = client.post(endpoint,json=payload,headers=HEADERS).status_code
    sandbox.failing = True
    calls_before = sandbox.calls
    failed = client.post(endpoint,json={**payload,"operator_token":"review-only-not-a-secret"},headers=HEADERS).json()
    export_status = client.get(f"/api/runs/{failed['id']}/comparison").status_code
    quarantined = not client.get("/api/health").json()["docker"]["available"]
    unchanged = before == client.get(f"/api/runs/{baseline['id']}").content
    record("live_scenario_auth_and_failure",passed=auth_status==403 and failed["status"]=="failed" and
        failed["summary"] is None and export_status==404 and sandbox.calls-calls_before==1 and quarantined and unchanged,
        auth_status=auth_status,status=failed["status"],export_status=export_status,sandbox_calls=sandbox.calls-calls_before,
        quarantine=quarantined,baseline_unchanged=unchanged)

files = ("prooflane/app.py","prooflane/provider.py","prooflane/comparison.py","prooflane/sandbox.py",
         "prooflane/analysis.py","prooflane/receipts.py","prooflane/store.py","scripts/verify_receipt.py",
         "README.md","TESTING.md","FINAL_REPORT.md","SECURITY.md","docs/ARCHITECTURE.md","docs/SCENARIO_CONTRACT.md")
fingerprints = {file:hashlib.sha256((ROOT/file).read_bytes()).hexdigest() for file in files}
output = {"scope":"INDEPENDENT_CYCLE2_LOCAL_DOUBLES_OFFLINE_CLI_NOT_VSI", "passed":all(r["passed"] for r in records),
          "file_sha256":fingerprints, "checks":records}
(OUT/"engineering-cycle2-probes.json").write_text(json.dumps(output,indent=2),encoding="utf-8")
print(json.dumps({"passed":output["passed"],"checks":[{k:v for k,v in r.items() if k != "output"} for r in records]},indent=2))
