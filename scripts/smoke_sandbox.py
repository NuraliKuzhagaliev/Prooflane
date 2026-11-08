"""Run real local Docker checks; does not test Vultr hosting or inference."""
from pathlib import Path
import json
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prooflane.sandbox import DockerSandbox, SandboxError

def main():
    sandbox = DockerSandbox()
    report = {"scope": "REAL_LOCAL_DOCKER_NOT_VULTR", "at": datetime.now(timezone.utc).isoformat(),
              "health": sandbox.available(), "tests": []}
    try:
        execution = sandbox.run("import csv,json\nfrom decimal import Decimal\nrows=list(csv.DictReader(open('/tmp/input.csv')))\nprint(json.dumps({'variance':str(sum((Decimal(r['unit_price'])-Decimal(r['contract_price']))*int(r['quantity']) for r in rows))}))",
                                "quantity,unit_price,contract_price\n3,12.50,10.00\n")
        report["tests"].append({"name": "CSV arithmetic", "passed": json.loads(execution["stdout"])["variance"] == "7.50" and execution["cleanup"], "execution": execution})
        report["probe"] = sandbox.probe()
        for name, code in [("Timeout", "while True: pass"), ("Output cap", "import sys\nwhile True: sys.stdout.write('x'*4096);sys.stdout.flush()")]:
            try:
                sandbox.run(code, "", timeout=1 if name == "Timeout" else 5)
                report["tests"].append({"name": name, "passed": False, "detail": "Expected rejection did not occur."})
            except SandboxError as exc:
                expected = "wall-clock" if name == "Timeout" else "output exceeded"
                report["tests"].append({"name": name, "passed": expected in str(exc) and exc.execution.get("cleanup") is True, "detail": str(exc), "execution": {k:v for k,v in exc.execution.items() if k not in {"stdout", "stderr"}}})
        report["passed"] = report["probe"]["passed"] and all(t["passed"] for t in report["tests"])
    except (SandboxError, ValueError, KeyError) as exc:
        report.update(passed=False, error=str(exc))
    destination = Path(__file__).resolve().parents[1] / "artifacts" / "sandbox-smoke.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "evidence": str(destination)}, indent=2))
    return 0 if report["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
