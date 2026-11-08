# Working on this project

Goal: Prooflane — receipt-linked invoice variance analysis with isolated Vultr code execution.

Categories: ai-ml, backend, cybersecurity, frontend, full-stack, hackathon, llm-agents.
Mode: hackathon. Scope: this project only; do not modify adjacent projects.

## Stack and architecture
- Python 3.13
- FastAPI + Uvicorn
- Vanilla JavaScript + CSS
- SQLite
- Docker on a dedicated Vultr VM
- Vultr Serverless Inference
- Same-origin browser and API with session-isolated runs
- Generated Python executes only in disposable offline containers without secrets or host mounts
- Independent Decimal verifier checks every price-variance row
- Hash-linked JSON receipt binds input, code and output; hashes are integrity evidence, not proof of truth
- Explicit reference mode computes trusted fixed rules without pretending to be AI

## Available processes
- `$hub-hackathon` — ON_DISK
- `$hub-research` — ON_DISK
- `$hub-innovation` — ON_DISK
- `$hub-engineering` — ON_DISK

Details and conditional roles: `.bootstrap/runs/`, `plan.json` and `capabilities.json`.
Load only the necessary skill and dependencies. Review roles read original evidence;
their instructions do not create a separate sandbox.

## Quality and constraints
- Upload a valid invoice CSV, execute analysis, inspect source rows and download a verifiable receipt
- Reject malformed or mismatching model output
- Refuse generated code when Docker is unavailable
- Docker runs have no network, host mounts or injected credentials; resource caps and cleanup
- Show honest execution provenance in the browser
- All tests and evidence recorded without simulated integration claims
- Budget $0; existing Vultr credits reported by user; no new charged resources without scope
- Project and caches on D:
- No infrastructure-global edits
- Exact deadline/timezone UNKNOWN in the original bootstrap instructions; current observed schedule is recorded separately in docs/RULES.md
- Cloud and model gates remain NOT_RUN until actual access and tests

Keep secrets outside source control. Preserve licenses and data/asset provenance.
Record actual commands, results and limitations. Do not invent measurements,
sources, scientific novelty or organizer/university requirements.

## Checks
- `.venv/Scripts/python.exe -m pytest -q`
- `python C:/Users/nural/.agents/skills/project-bootstrap/scripts/bootstrap.py verify --project D:/projects/vultre`
- `python scripts/verify_receipt.py RECEIPT.json`
- `python scripts/smoke_sandbox.py`

Distinguish structural verification from application execution, experiments and browser checks.
Read existing instructions in affected subdirectories first.
