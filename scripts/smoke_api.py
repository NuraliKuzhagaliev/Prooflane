"""Exercise the running local service; only the bundled synthetic CSV is uploaded."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prooflane.receipts import check_receipt


def main():
    url = "http://127.0.0.1:8765"
    evidence = {"scope": "REAL_LOCAL_HTTP_AND_DOCKER_NOT_VULTR", "at": datetime.now(timezone.utc).isoformat(), "tests": []}
    def check(name, condition):
        evidence["tests"].append({"name": name, "passed": bool(condition)})
        assert condition, name
    with httpx.Client(base_url=url, timeout=60, trust_env=False) as client:
        health = client.get("/api/health").json()
        evidence["health"] = health
        check("static assets", all(client.get(p).status_code == 200 for p in ["/", "/static/app.js", "/static/styles.css"]))
        sample = client.get("/api/sample").json()
        for mode in ["reference", "sandbox"]:
            response = client.post("/api/runs", headers={"X-Prooflane-Request":"1"}, json={"csv":sample["csv"],"filename":sample["filename"],"mode":mode})
            check(mode + " request", response.status_code == 200)
            run = response.json()
            check(mode + " result", run["status"] == "verified" and run["summary"]["total_variance"] == "1480.00")
            receipt = client.get(f"/api/runs/{run['id']}/receipt").json()
            check(mode + " receipt verification", check_receipt(receipt)["passed"])
            (ROOT / "artifacts" / f"{mode}-receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
            if mode == "sandbox":
                evidence["sandbox_elapsed_ms"] = run["execution"]["elapsed_ms"]
                check("sandbox cleanup", run["execution"]["cleanup"] is True)
            with httpx.Client(base_url=url, trust_env=False) as stranger:
                check(mode + " cross-session isolation", stranger.get(f"/api/runs/{run['id']}").status_code == 404)
        check("invalid CSV rejected", client.post("/api/runs", headers={"X-Prooflane-Request":"1"}, json={"csv":"bad"}).status_code == 422)
        check("CSRF marker enforced", client.post("/api/runs", json={"csv":sample["csv"]}).status_code == 403)
    evidence["passed"] = all(t["passed"] for t in evidence["tests"])
    (ROOT / "artifacts" / "api-smoke.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    (ROOT / "artifacts").mkdir(exist_ok=True)
    main()
