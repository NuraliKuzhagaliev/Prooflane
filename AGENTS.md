# Работа над проектом

Цель: Prooflane: receipt-linked invoice variance analysis with isolated Vultr code execution

Категории: ai-ml, backend, cybersecurity, frontend, full-stack, hackathon, llm-agents.
Режим: hackathon. Рабочая область: текущий проект; соседние проекты не изменять.

## Стек и архитектура
- Python 3.13
- FastAPI + Uvicorn
- vanilla JavaScript + CSS
- SQLite
- Docker on a dedicated Vultr VM
- Vultr Serverless Inference
- Same-origin browser and API with session-isolated runs
- Generated Python executes only in disposable offline containers without secrets or host mounts
- Independent Decimal verifier checks every price-variance row
- Hash-linked JSON receipt binds input, code and output; hashes are integrity evidence, not proof of truth
- Explicit reference mode computes trusted fixed rules without pretending to be AI

## Доступные процессы
- `$hub-hackathon` — ON_DISK
- `$hub-research` — ON_DISK
- `$hub-innovation` — ON_DISK
- `$hub-engineering` — ON_DISK
Подробности и условные роли: `.bootstrap/runs/`, файлы `plan.json` и `capabilities.json`.
Загружать только нужный навык и его зависимости. Проверяющие роли читают исходные
доказательства; их инструкции не создают отдельную песочницу.

## Качество и ограничения
- Upload a valid invoice CSV, execute analysis, inspect source rows and download a verifiable receipt
- Reject malformed or mismatching model output
- Refuse generated code when Docker is unavailable
- Docker runs have no network, host mounts or injected credentials; resource caps and cleanup
- Show honest execution provenance in the browser
- All tests and evidence recorded without simulated integration claims
- Budget $0; existing Vultr credits reported by user; no new charged resources without scope
- Project and caches on D:
- No infrastructure-global edits
- Exact deadline/timezone UNKNOWN
- Cloud and model gates remain NOT_RUN until actual access and tests
Хранить секреты вне исходников. Сохранять лицензии и происхождение данных/ассетов.
Фиксировать реальные команды, результаты и ограничения; не придумывать измерения,
источники, научную новизну или требования организаторов/университета.

## Проверки
- .venv/Scripts/python.exe -m pytest -q
- python C:/Users/nural/.agents/skills/project-bootstrap/scripts/bootstrap.py verify --project D:/projects/vultre
- python scripts/verify_receipt.py RECEIPT.json
- python scripts/smoke_sandbox.py
Отличать структурную проверку от запуска приложения, эксперимента и браузера.
Сначала изучать существующие инструкции в затрагиваемых подкаталогах.
