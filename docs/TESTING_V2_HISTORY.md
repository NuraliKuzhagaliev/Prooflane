# Выполненные проверки

Дата: 2026-11-03, Asia/Qyzylorda. Проверен локальный прототип. Реальный Vultr Serverless Inference и облачный deployment не проверены.

## Текущий проход: сценарии одного допущения

Не суммировать разные виды проверок в «accuracy». Unit/API doubles, настоящий HTTP/Docker, browser и реальные пользователи — разные уровни доказательств.

| Проверка | Фактический результат | Доказательство |
|---|---|---|
| Windows Python suite после provider Unicode fix | **83 PASS**, 1 deprecation warning | [windows-cycle1.txt](../artifacts/optimization/windows-cycle1.txt) |
| Пересобранный Linux validation image после того же fix | **83 PASS**, 1 deprecation warning | [linux-final.txt](../artifacts/optimization/linux-final.txt), [build](../artifacts/optimization/linux-build.txt) |
| Decimal string formatting JS | **6 PASS**, включая signed delta и большие суммы | [node-final.txt](../artifacts/optimization/node-final.txt) |
| Ручные CSV-oracles через настоящий HTTP, reference и Docker | **24/24 PASS**, 16 проверенных receipts, 0 model calls | [evaluation.json](../artifacts/optimization/evaluation.json) |
| Baseline→scenario→download→offline CLI через настоящий HTTP | **36/36 PASS**, по одной паре в reference и Docker | [scenario-smoke.json](../artifacts/optimization/scenario-smoke.json) |
| Настоящие Docker controls/containment/timeout/output cap/cleanup | PASS, повторены после изменений | [sandbox-smoke.json](../artifacts/sandbox-smoke.json) |
| Python compileall, JavaScript syntax, pip check | PASS | Команды ниже; это не browser/runtime evidence |
| Браузерная интеграция автора | PASS reference1480→1160 и sandbox1480→960, download, stale draft, mobile320/390 | [frontend-implementation.md](../artifacts/optimization-review/frontend-implementation.md) |
| Независимый engineering cycle1 и повтор воспроизведённых ошибок | E1/E2/E3 исправлены и перепроверены | [engineering-cycle1.md](../artifacts/optimization-review/engineering-cycle1.md) |
| Независимая проверка сравнения со стороны judge | Обе арифметики и отрицательные контроли PASS; готовность условная | [judge-cycle1.md](../artifacts/optimization-review/judge-cycle1.md) |
| Второй независимый engineering cycle на зафиксированном коде | **16/16 PASS**, новых дефектов не найдено | [engineering-cycle2.md](../artifacts/optimization-review/engineering-cycle2.md) |
| Повторный настоящий HTTP/Docker scenario после restart | **36/36 PASS**, отдельные новые runs и packets | [final/scenario-smoke.json](../artifacts/optimization/final/scenario-smoke.json) |
| Независимая browser-проверка cycle1 | Полный flow, downloads, stale inputs,600/601 и mobile PASS | [ux-cycle1.md](../artifacts/optimization-review/ux-cycle1.md) |
| Независимая browser-проверка cycle2 после freeze/restart | Native file upload, invalid CSV recovery, новый Docker original/scenario, download→CLI, history/mobile/keyboard PASS; новых дефектов не найдено | [ux-cycle2.md](../artifacts/optimization-review/ux-cycle2.md) |
| Второй judge review | Локальное поведение PASS; cloud/подписание/бизнес-превосходство не заявляются | [judge-cycle2.md](../artifacts/optimization-review/judge-cycle2.md) |

Сводный [validation-summary.json](../artifacts/optimization/validation-summary.json) связывает исходную ревизию, SHA-256 файлов и отдельные доказательства. В одном локальном прогоне восьми успешных CSV-cases медиана полного HTTP-case составила19.59ms в reference и2019.69ms в Docker; диапазоны16.38–24.74ms и1962.90–2495.05ms. Это включает загрузку receipt и ownership checks, не является нагрузочным benchmark, обещанием latency или сравнением облачных платформ.

Новый доверенный результат: synthetic record3 `contract_price72→80`, original1480, scenario1160, delta−320, row520→200, billed34353 без изменения,23 другие записи прежние. [Полный Docker packet](../artifacts/optimization/sandbox-comparison.json) и [reference packet](../artifacts/optimization/reference-comparison.json) проверяются одной CLI. Отдельный browser сценарий72→85 даёт row520→0, total960,5findings: исчезнувшая находка остаётся видима в сравнении.

Регрессии нового кода проверяют скрытые изменения notes/vendor/другой цены, подмену parent/hash/mode/delta, no-op, неверные диапазоны, чужую сессию, CSRF, failed scenario без экспорта и сохранность baseline. Provider tests используют MockTransport, не живую модель. Clean timeout разрешает единственную repair-попытку; uncertain cleanup повтор не разрешает. Неправильная оболочка и escaped surrogate в plan/model/code отклоняются без исполнения. Независимые probes отдельно воспроизвели ошибку Unicode до fix и проверили её после fix.

Повторить доступные проверки:

```powershell
.venv/Scripts/python.exe -m pytest -q --tb=short
node --test tests/test_format.mjs
.venv/Scripts/python.exe scripts/smoke_scenario.py
.venv/Scripts/python.exe scripts/evaluate_csv.py --output artifacts/optimization/evaluation.json
.venv/Scripts/python.exe scripts/verify_receipt.py artifacts/optimization/sandbox-comparison.json
.venv/Scripts/python.exe scripts/smoke_sandbox.py
node --check web/app.js
node --check web/scenario.js
.venv/Scripts/python.exe -m compileall -q prooflane scripts tests
.venv/Scripts/python.exe -m pip check
```

HTTP-команды требуют работающего сервера и Docker; выполняют только synthetic данные, не вызывают модель. Лимиты запросов приложения действуют и во время многократной репетиции. `83` — количество Python test cases, а не 83 отдельных реальных контейнера. Предыдущий Linux cycle1 имел80tests; он сохранён как предыдущий срез и не выдается за final83.

**Непроверено:** live VSI и его repair quality, Vultr VM/HTTPS, внешний judge без локального окружения, финальное видео, нагрузка нескольких пользователей, process SIGKILL, OOM stress, полный screen-reader/contrast аудит и человеческое исследование ценности. Hash verifier не доказывает авторство/исполнение; сравнение с конкурентами не является benchmark.

Ниже сохранена история предыдущих проверок; актуальный набор выше.

## Дополнение: независимые данные и точность интерфейса

После отправки billing ticket выполнен новый прогон:

- `pytest -q --tb=short`: **53 PASS** на Windows Python 3.13.2; **53 PASS** в пересобранном Linux validation container. Добавлено 15 checks: 12 CSV-cases через TestClient и отрицательные проверки самого evaluator. TestClient не подменяет фактический HTTP-прогон ниже.
- `node --test tests/test_format.mjs`: **4 PASS**, включая верхние границы сумм, обычные центы, нули и неверные значения.
- `scripts/evaluate_csv.py --output artifacts/evaluation-local.json`: **24/24 PASS** через работающий HTTP-сервер: 8 правильных и 4 неправильных CSV в каждом из reference/sandbox. Выполнено 8 настоящих Docker analyses; 16 успешных receipts проверены на ввод, ожидаемые значения, хеши, режим, runtime и изоляцию сессий. [Машинный отчёт](../artifacts/evaluation-local.json), [расчёты вручную](examples/evaluation/README.md).
- Отрицательный контроль evaluator: в памяти намеренно заменено ожидаемое `0.60` на `0.59`; настоящий HTTP run отвергнут, `main()` вернул **1**, FAIL сохранён в [отдельном отчёте](../artifacts/evaluation-negative-control.json). Канонический `cases.json` не изменялся.
- CUA browser: новый ES module загружен; sandbox run `4b648b71-6659-44ed-9748-c18d905182bc` вернул одну строку, `$9,999.99` positive variance и точное отображение `$99,999,899,990,000.01` billed. Cleanup confirmed. При естественной узкой панели browser `innerWidth=455`, `documentElement.scrollWidth=440`; горизонтального переполнения страницы нет, длинное число переносится. [Скрин](../artifacts/screenshots/large-amount-fixed.jpg).
- Основной sample повторён в обновлённом браузере: run `72513657-72e8-4353-8c74-7cade453febf`, 24 записи / 6 findings / `$1,480.00` / `$34,353.00`, Docker cleanup confirmed. [Готовая локальная демонстрация](../artifacts/screenshots/offline-demo-ready.jpg).

Обнаруженный дефект: прежний `Number(decimalString)` перед Intl округлял допустимое значение `99999899990000.01` до отображаемого `...000.02`. Исправление группирует разряды и дополняет дробную часть непосредственно в десятичной строке. Во время проверки расширение `.mjs` на данном Windows-хосте отдавалось как `text/plain` и не запускалось браузером; модуль переименован в `.js`, загрузка и основной workflow повторно проверены. Числовая арифметика backend не менялась.

Новые данные с инструкциями в notes проверяют обращение с текстом как с данными; raw CSV не отправляется LLM, поэтому это не оценка стойкости реальной модели. Оценка модели, запуск на Vultr и пользовательское интервью всё ещё NOT_RUN. Ниже сохранены результаты предыдущего прогона из 38 тестов как история проверки.

| Команда / проверка | Результат | Доказательство / граница |
|---|---|---|
| `.venv\Scripts\python.exe -m pytest -q --tb=short` | PASS: 38 tests | Windows Python 3.13.2; arithmetic, API, ownership, validation, quarantine, provider contract, bounded retry, sandbox control tests |
| `docker build --pull=false -f Dockerfile.validation -t prooflane-validation:local .` | PASS | Чистая установка requirements.lock в Linux Python 3.13 |
| `docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges=true --memory 512m --cpus 2 --pids-limit 128 --tmpfs /tmp:rw,nosuid,size=64m prooflane-validation:local` | PASS: 38 tests | [Linux output](../artifacts/linux-tests.txt); без сети/host mounts, от непривилегированного пользователя |
| `docker build --pull=false -t prooflane-sandbox:local sandbox` | PASS | Закреплённый Python image digest; собственный минимальный runner |
| `.venv\Scripts\python.exe scripts\smoke_sandbox.py` | PASS | [Реальный Docker smoke](../artifacts/sandbox-smoke.json): CSV, actual controls, containment, timeout, output cap, cleanup |
| `.venv\Scripts\python.exe scripts\smoke_api.py` | PASS: 12 assertions | [HTTP smoke](../artifacts/api-smoke.json): реальные HTTP и Docker; model calls отсутствуют |
| `.venv\Scripts\python.exe scripts\verify_receipt.py artifacts\browser-receipt.json` | PASS | Файл скачан кнопкой браузера; хеши + независимый пересчёт $0.60 для изменённых данных |
| `node --check web/app.js` | PASS | Синтаксис JavaScript, не замена браузерного теста |
| `.venv\Scripts\python.exe -m compileall -q prooflane scripts tests` | PASS | Синтаксис Python |
| `.venv\Scripts\python.exe -m pip check` | PASS | No broken requirements |
| `.venv\Scripts\python.exe -m pip_audit --disable-pip --no-deps -r requirements.lock --cache-dir .cache\pip-audit --format json --output artifacts\dependency-audit.json` | PASS: no known vulnerabilities | [23 pinned Python packages](../artifacts/dependency-audit.json); это не скан Linux image и не гарантия безопасности |
| `python C:/Users/nural/.agents/skills/project-bootstrap/scripts/bootstrap.py verify --project D:/projects/vultre` | PASS | Только структура bootstrap и сохранность guidance |

`httpx` в текущем Starlette TestClient выдаёт deprecation warning о будущей миграции на httpx2; тесты проходят. Audit tooling pip-audit установлен только локально и не добавлен в application lock.

## Браузерная проверка

Через CUA, настоящий Chromium в in-app browser, локальный сервер и Docker:

- Synthetic sample → Sandbox recipe → 24 records / 6 findings / $1,480.00 variance / $34,353.00 billed.
- Открытие INV-2402: источник record 3, `(85-72)*40 = 520`; Escape закрывает dialog и возвращает focus.
- Containment action: network probe, root write, credential variable absence, UID65534 и cleanup показали PASS. Эти частные пробы не доказывают невозможность escape.
- Неверный CSV показывает конкретную ошибку структуры и не сохраняет непроверенные итоги.
- Изменённый CSV: три единицы по $0.30 вместо $0.10 и отдельная строка с отрицательной разницей → $0.60 positive variance, $1.10 billed. Строка `<b>ACME</b>` отображается буквальным текстом.
- Кнопка Download receipt действительно скачивает JSON; копия сохранена в [browser-receipt.json](../artifacts/browser-receipt.json) и проверена CLI.
- Viewports 1440×1000 и 390×844: `document.documentElement.scrollWidth <= innerWidth`. Временный viewport override сброшен.
- Console errors при финальной проверке: пустой список. Полный accessibility audit, screen reader, Firefox/Safari и реальный мобильный девайс: NOT_RUN.

Скриншоты: [desktop](../artifacts/screenshots/desktop-review.jpg), [mobile](../artifacts/screenshots/mobile-review.jpg), [source record](../artifacts/screenshots/source-record.jpg). CUA JPEG на широком viewport мягкий; данные и расположение проверены также через accessibility tree.

## Отрицательные результаты и исправления

1. `venv ensurepip` сначала упал из-за временной директории Windows sandbox. TEMP/TMP перенесены в `.cache/tmp` на D:, окружение восстановлено.
2. Network install внутри AppContainer: DNS failure; установлены пакеты с разрешённым внешним доступом только в project venv.
3. Docker daemon первоначально недоступен; установленный Docker Desktop запущен. Глобальная конфигурация не менялась.
4. Первый sandbox smoke обнаружил непреодолимые права `/opt/prooflane`; Dockerfile исправлен, сборка/smoke повторно PASS.
5. API tests внутри AppContainer зависали в Python asyncio socketpair до исполнения приложения; стек сохранён в истории работы. Тот же suite вне этой границы и в Linux PASS.
6. Независимый review воспроизвёл отсутствие блокировки после cleanup failure, Unicode CSV500 и Unicode token500. Исправления проверены отдельно reviewer и regression tests. Добавлен persisted quarantine и startup stale-container gate.
7. Первый Unicode fix не устранил ошибку сериализации стандартного FastAPI validation handler. Добавлен безопасный 422 handler без echo пользовательских значений; повторно PASS.

Независимые исходные/повторные результаты: [audit report](../artifacts/audit/REPORT.md), [before](../artifacts/audit/reproduction-before.json), [after](../artifacts/audit/reproduction.json).

## Непроверенные gates

Vultr VM/HTTPS/живой VSI, качество генерации на конкретной модели, настоящий repair после model failure, end-to-end с GPU (не требуется), SIGKILL процесса в критический момент, память под OOM-нагрузкой, длительная нагрузка/параллельные пользователи, окончательное конкурсное видео, публикация GitHub/lablab: NOT_RUN или BLOCKED по внешнему доступу. Provider mock и retry doubles не являются живыми AI-вызовами.

Один финальный Docker HTTP smoke измерил 1420.63ms от создания контейнера до cleanup для synthetic24rows. Это единичное локальное наблюдение, без LLM/network latency и без p95/SLA/бизнес-эффекта.
