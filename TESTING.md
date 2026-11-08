# Проверки текущего case workbench

## Живой AI через публичную форму, 9 ноября 2026

**PASS:** browser → Vultr `deepseek-v4.1-flash-1017` → generated Python → Docker → independent verification → Vultr explanation → downloaded packet. Успешный run `93ccc09e-5289-402d-b7b8-41be8c8e958e`,7из8 строк, USD768.00,2 модельных вызова, exit0/cleanup=true. Браузерный и CLI verifier приняли7групп; reload сохранил дело/AI-mode. [Полный отчёт](docs/LIVE_AI_CHECK_20261109.md) · [Proof](artifacts/live-ai-20261109/live-proof.jpg).

Первый живой запрос был incomplete и корректно остановлен до Docker. После явного отключения дефолтного reasoning для bounded JSON DeepSeek V4.1 повтор прошёл. Максимумы токенов4096/1024 не повышались, fallback отсутствует. **179 Python PASS**, **26 JavaScript PASS**, одно прежнее предупреждение. Временный operator token-файл удалён; API-ключ остался на VM.

## Усиление по шести направлениям, 8 ноября 2026

[Полный итоговый отчёт](docs/TRANSFORMATION_RESULT_20261108.md) фиксирует18 отдельных изменений, источники, оба независимых ревью и ограничения. **176 Python PASS**, одно существующее предупреждение Starlette; **25 JavaScript PASS**, syntax/diff PASS. В новом окружении из lockfile `pip check` и15 targeted тестов с новыми SQLite прошли; Uvicorn из него запущен на8766. Структурный bootstrap отдельно PASS.

Публичные HTTP-прогоны: **57 case checks** Reference/Docker и **23 review checks** с настоящим Docker. [Case](artifacts/transformation-20261108/public-case/case-http-smoke.json) · [Review](artifacts/transformation-20261108/public-review/sandbox-review-smoke.json). Новых обращений к модели0. Повтор UUID возвращает те же case/run, изменённый запрос409, чужая session404. Сырая неоднозначная JSON-структура отвергается; обычный packet принимается.

Реальный browser walkthrough на публичном сайте: malformed header→сохранённый ввод→исправление+дублирующая строка→warning→ручные исключения→Docker baseline768→C1=80 alternative368→CSV/brief/packet download. Скачанный packet прошёл7групп CLI; CSV сохранил9источников/2исключения/768 variance, brief сохранил quality-warning. Отдельно проверены one-click Reference, Enter, reload, public containment5PASS, desktop1280/tablet900/mobile390и320 без page overflow. [Кадр мобильных альтернатив](artifacts/transformation-20261108/after-alternatives-mobile.jpg). Physical touch, screen reader listening и системное переключение reduced motion в этом цикле NOT_RUN.

CPU benchmark500invoices/500contracts,2warmup/9samples: match22.793→9.060мс, explore24bounds529.871→9.247мс; хеши полного ответа совпали. Это не интернет-латентность. [Сырые результаты](artifacts/transformation-20261108/performance-after.json).

## Порог смены приоритета, 8 ноября 2026

- Python: **161 PASS**, одно существующее предупреждение Starlette; полный запуск с отдельным `--basetemp` и разрешённым Windows loopback. JavaScript: **17 PASS**, `node --check web/workbench.js` прошёл. Новый математический тест сравнивает границы и соседние состояния с независимым перебором 576 малых сеток, включая общие договоры и повторяющиеся ID счетов. Проверено отклонение семантической подмены с пересчитанным хешем и принятие исторического пакета без нового поля.
- Шесть файлов опубликованы на существующей VM с проверкой SHA-256 `1e6a84ea70f3eadbe5bfb12cc76f739011be5c1ed96e198ab243807bb4482650` и резервной копией. Health после запуска подтвердил Docker и включённую конфигурацию Inference. Секреты и настройки Inference не изменялись.
- `.venv/Scripts/python.exe scripts/smoke_case.py --base-url https://45.76.92.198 --output-dir artifacts/priority-release` — **57 PASS**: настоящий HTTPS, Reference и Docker, **0 модельных вызовов**. [Отчёт](artifacts/priority-release/case-http-smoke.json).
- В IAB на публичном сайте пройден новый сценарий: fictional CSV → выбор C2R → явное исключение INV506 → Sandbox recipe baseline **$768.00** → карточка порога → подготовка C1 **$82.60** → Add change → запуск именованной альтернативы **$244.00**. Baseline сохранён, альтернативу независимо проверил сервер. Три состояния карточки: **$82.59 INV501**, **$82.60 ничья INV501/INV503**, **$82.61 INV503**.
- Скачанный через интерфейс [пакет с одной альтернативой](artifacts/priority-release/browser-case-packet.json) принят CLI: **7 групп PASS**, включая восстановление порога. [Desktop](artifacts/priority-release/priority-switch-desktop.jpg) и [mobile](artifacts/priority-release/priority-switch-mobile.jpg) — реальные кадры. На viewport 390px документ и область содержимого имели одинаковую ширину 375px, новая кнопка — высоту 44px. Enter подготовил цену и перевёл фокус в её поле. В журнале браузера не наблюдалось ошибок.
- Проверка project-bootstrap — **STRUCTURAL_ONLY PASS**, отдельно от перечисленных выполнений. Физический touch, чтение экранным диктором, новое живое обращение к модели и пользовательское исследование в этом цикле **NOT_RUN**. Новых анимаций нет; карточка не делает прогнозов и сохраняет остальные поля на исходных значениях.

## Живой Vultr Serverless Inference, 6 ноября 2026

- На публичном HTTPS включён режим `Vultr agent` с моделью `deepseek-v4.1-flash-1017`. Запрос `/api/cases` на вымышленном примере завершился на сервере HTTP 200. Первый клиент получил таймаут при чтении ответа. Пакет тестового кейса восстановлен с VM и прошёл все шесть групп офлайн-проверки. [Пакет](artifacts/vultr-release/live-recovered-case-packet.json) · [Отчёт с ID Vultr](artifacts/vultr-release/live-evidence.json).
- Зафиксированы два запроса к модели, один для генерации Python и один для объяснения. Docker обработал 7 из 8 строк и подтвердил удаление контейнера. Проверенное положительное отклонение составило $768.00.
- Запуск без operator token вернул 403. Все пять проверок изоляции прошли при включённом Inference, включая проверку отсутствия переменной ключа в контейнере. [Отчёт](artifacts/vultr-release/live-boundary-checks.json).
- В Caddy включено сжатие `zstd gzip`. После этого HTML и оба основных скрипта загружались целиком за 1.5–3.1 с при проверке `curl.exe --compressed`. Автоматизация Chrome и встроенного браузера прерывалась по таймауту, полный прогон формы не завершён.

## Agent Rush release, 6 ноября 2026

- Последнее обновление проверено на VM Vultr и развернулось с резервной копией четырёх исходных файлов. SHA-256 архива `cb304a44c85839dea2541c908d4d8b715a3cd67a6cb8ec3365c6df3657534ec3`. Health показал доступный Docker, указанную модель `deepseek-v4.1-flash-1017`, `configured=false` и `enabled=false`. Ключ подписки в серверной конфигурации отсутствует.
- Python: **156 PASS**, одно предупреждение Starlette. Первый прогон под песочницей Windows завис на loopback-сокете; повтор с разрешённым loopback и отдельным `--basetemp` прошёл. JavaScript: **17 PASS**. Проверка project-bootstrap прошла в режиме `STRUCTURAL_ONLY`.
- `.venv/Scripts/python.exe scripts/smoke_case.py --base-url https://45.76.92.198 --output-dir artifacts/vultr-release` прошёл **53 проверки** на публичном HTTPS. Это настоящий Docker и Reference, ноль вызовов модели. Проверены $768 baseline, $368 shared price, $568 joint alternative, точные границы $148–$1,993, офлайн-воспроизведение, отклонение правки с пересчитанным хешем и изоляция сессий. [Отчёт](artifacts/vultr-release/case-http-smoke.json).
- Chrome на публичном сайте запустил проверку изоляции из вкладки Proof. Все пять проверок прошли. [Снимок](artifacts/vultr-release/containment.jpg). Отдельные наблюдения относятся к этому запуску, без обобщения на произвольные атаки.
- Проверены импорт PPTX, две редактируемые таблицы и рендер всех шести страниц [конкурсного PDF](submission/agent-rush/prooflane-deck.pdf). Полный живой тест VSI и финальное видео ожидают ключа.

## Публичный запуск на Vultr, 6 ноября 2026

- Релиз `prooflane-release-20261106.tar.gz`, SHA-256 `db64ecade9ac73b0e6b3dcc092311c23f87622617eb292c8f77a0c728b1b8faa`. Службы `prooflane` и `caddy` активны. Caddy проксирует приложение на `127.0.0.1:8765`. В UFW добавлены TCP 80 и 443.
- Внешний запрос `curl.exe -I http://45.76.92.198/` получил 308 с переходом на HTTPS. `curl.exe -fsS https://45.76.92.198/api/health` прошёл с проверкой сертификата и вернул `docker.available=true`, `inference.enabled=false`.
- Chrome на публичном HTTPS прошёл сверку встроенного вымышленного примера в режиме Sandbox recipe. После выбора договора для INV504 и исключения INV506 расчёт включил 7 из 8 строк и показал $768.00 отклонения. В пакете зафиксированы Docker, код выхода 0, удаление контейнера, отключённая сеть и отсутствие монтирований с хоста. [Скриншот результата](artifacts/vultr-prooflane-ledger.jpg).
- Скачанный пакет `prooflane-case-15772d93-2422-4e55-bb93-1784815d9f6e.json`, SHA-256 `bb15e1f5f3397476d512d44dc485ddf3e48074845ec2fa17b746495bfd5c65fc`, проверен через `.venv/Scripts/python.exe scripts/verify_receipt.py <packet.json>`. Результат `passed: true`, шесть групп проверок, ноль альтернатив.

## Палитра и доступность Audit Folio, 6 ноября 2026

- Chrome до изменений. Enter на INV506 открыл запись, но оставил фокус на `BODY`. Оба поля загрузки были озаглавлены одинаково. Добавлены отдельные имена, переход к заголовку записи и возврат к заменённой строке либо к поиску, если строка отфильтрована.
- `node --test tests/test_*.mjs` дал 17 PASS. Проверка перехода фокуса выполняет обработчик выбора строки с заменой узлов в тестовой DOM-модели. `node --check web/workbench.js` и `git diff --check` прошли.
- `.venv/Scripts/python.exe -m pytest -q` дал 155 PASS и одно предупреждение Starlette. Первый ограниченный запуск остановлен после зависания, результат указан для повторного полного запуска.
- Локальный HTTP вернул обновлённые HTML, CSS и JS. Сверка синтетических файлов показала 2 нерешённых совпадения, после решений включила 7 из 8 записей и рассчитала $768. Экспортированный пакет прошёл проверку API. Проверка project-bootstrap прошла в режиме `STRUCTURAL_ONLY`.
- Проверка HTML нашла 253 уникальных ID, действительные статические ссылки ARIA и отсутствие косых черт в статичных надписях. Расчёт контраста шести пар палитры дал от 5,96 до 12,92 к 1. Для reduced motion проверено наличие правил CSS, включая запуск эффекта только при `no-preference`. Эти проверки не измеряют отрисовку или анимацию браузера.
- Экранный диктор, жесты, системный reduced motion и визуальный проход по новой версии остаются `NOT_RUN`. Инструмент остановил управление Chrome, поскольку при переходе к окну Windows не смог уверенно определить URL. По публичному IP из снимка Vultr запросы HTTP и HTTPS превысили таймаут. Снимок показывает `Stopped`, работа приложения на VM не подтверждена.

## Audit Folio — 5 ноября 2026

Новая оболочка и переходы проверены отдельно от исторических прогонов ниже. Python **155 PASS**, JavaScript **16 PASS**, существующие async/failure-пробы **12 групп PASS**. Структурная проверка project-bootstrap **PASS** проверяет только файлы и guidance. Настоящие браузерные циклы: source decisions → baseline768 → диапазоны148..1993 → packet; первый независимый цикл также выполнил варианты368/568 и браузерную проверку скачанного пакета. Во втором root повторил исправленные source→Proof, ошибку/восстановление CSV и диапазона, клавиатурные вкладки, Archive Escape и legacy1480→1160.

Сделаны чистые реальные кадры desktop1440, tablet900, mobile390 и320px. Независимый критик сам работал в браузере в первом цикле; во втором независимо изучил кадры, исходники и запустил CLI, не выдавая действия root за свои. Последний case packet проверен CLI: **6 групп PASS**, в нём **0 alternatives**. Motion timing, screen reader, physical touch, cloud/model — NOT_RUN. Docker сейчас недоступен, новый sandbox smoke не выполнялся; исторические результаты ниже не перезаписаны. [Полный отчёт и ограничения](DESIGN_REPORT.md), [cycle2 review](artifacts/design-studio/critic-cycle2.md).

## Предыдущая функциональная трансформация — исторические результаты

4 ноября 2026. Проверен локальный продукт; реальный Vultr Serverless Inference и облачный deployment остаются NOT_RUN. Различаем unit/API doubles, настоящий HTTP/Docker, браузер и исследования с пользователями.

| Проверка | Результат | Доказательство |
|---|---|---|
| Windows Python regression | 155 PASS, один Starlette deprecation warning | [windows-final](artifacts/transformation/windows-final.txt) |
| Linux validation image, запуск без сети | 155 PASS, тот же warning | [linux-final](artifacts/transformation/linux-final.txt), [build](artifacts/transformation/linux-build-final.txt) |
| JS formatting и workbench model | 12 PASS | [node-final](artifacts/transformation/node-final.txt) |
| Source → case → два варианта → один/два диапазона → packet → CLI | 52/52 PASS через настоящий HTTP в reference и fixed Docker;0 model calls | [case-http-smoke](artifacts/transformation/case-http-smoke.json) |
| Прежний single-assumption API после restart | 36/36 PASS с настоящим Docker | [legacy scenario-smoke](artifacts/transformation/legacy/scenario-smoke.json) |
| Независимая математика | 216 полных малых boxes, внутренние значения, 2001-cent sweeps реальных packets | [science audit](artifacts/transformation-review/scientist-final.md), [oracle source](tests/test_intelligence_oracle.py) |
| Adversarial QA | 56 targeted cases PASS: source ambiguity, coverage, rehashed semantic forgeries, ownership, failure, expiry, revisions, concurrency, body limits | [QA](artifacts/transformation-review/qa-initial.md) |
| Principal engineer cycle1 | 29 backend probes; четыре воспроизведённых UI-дефекта исправлены | [cycle1](artifacts/transformation-review/engineering-cycle1.md) |
| Principal engineer cycle2 | 50 backend probes и12групп UI-state probes PASS; новая гонка чтения файлов исправлена | [cycle2](artifacts/transformation-review/engineering-cycle2.md) |
| Реальный browser cycle1 | Source decisions → baseline →3variants → ranges → downloadCLI → uploadverify → tamper rejection → history; клавиатура | [design-cycle1](artifacts/transformation-review/design-cycle1.md) |
| Реальный browser cycle2 | PASS: читаемые графики400/320px, два диапазона, actual file upload, draft invalidation/recovery, packetCLI, legacy1480→1160 и возврат | [design-cycle2](artifacts/transformation-review/design-cycle2.md) |
| Размер500invoices/500contracts/24ranges | CPU join+analysis:497.10,491.78,487.13ms; медиана491.78ms | [capacity](artifacts/transformation/capacity-calculation.json) |

Последнее измерение — три локальных последовательных вычисления, не load test, browser latency или сравнительный benchmark облаков. Independent UI probes выполняют фактические функции исходника в Node VM с управляемым transport/DOM; они не выданы за настоящий браузер. Provider tests используют doubles; sandbox case smoke использует настоящие контейнеры.

## Контрольные значения

Решения demo: invoice source5→C2R; source7 исключён с явной причиной. Семь из восьми строк в охвате. Baseline768.00, billed7110.00. Общая C1=80 меняет normalized rows2,3,8: variance368.00, delta−400.00. Совместно с quantity row2=80: variance568.00, delta−200.00, billed delta+3400.00. Baseline неизменен.

Один диапазон C1[65,85] даёт148.00..1193.00. Добавление quantity row2[20,80] даёт148.00..1993.00, ширину1845.00. Уточнение C1 даёт минимальное гарантированное сужение645.00 и возможное1845.00; quantity —0.00 и1200.00. C1 выше по гарантированному минимуму, не обязательно по выигрышу каждого возможного исхода.

Сохранены [reference](artifacts/transformation/reference-case.json), [Docker](artifacts/transformation/sandbox-case.json), [reference two-range](artifacts/transformation/reference-multi-range-case.json), [Docker two-range](artifacts/transformation/sandbox-multi-range-case.json). Все содержат synthetic sources. Verification не доказывает issuer, runtime или contract truth; код из packets не исполняется.

## Повторение

```powershell
.venv/Scripts/python.exe -m pytest -q --tb=short
node --test tests/test_format.mjs tests/test_workbench.mjs
node artifacts/transformation-review/principal-ui-probe.mjs
.venv/Scripts/python.exe artifacts/transformation-review/principal-backend-probe.py
.venv/Scripts/python.exe scripts/smoke_case.py
.venv/Scripts/python.exe scripts/smoke_scenario.py --output-dir artifacts/transformation/legacy
.venv/Scripts/python.exe scripts/verify_receipt.py artifacts/transformation/sandbox-multi-range-case.json
docker build -f Dockerfile.validation -t prooflane-validation:local .
docker run --rm --network none prooflane-validation:local
```

HTTP scripts требуют работающего localhost8765 и существующего sandbox image; они не вызывают модель. Quotas действуют при повторных прогонах. Логический24hсрок означает, что сохранённые HTTP case IDs со временем исчезают; скачанные файлы проверяются и после этого.

История предыдущей версии и containment checks сохранена в [TESTING_V2_HISTORY](docs/TESTING_V2_HISTORY.md) и исходных artifacts/optimization/. Старые83Python/6JScounts не выдаются за текущие. Контрольный Docker profile не изменён; его реальные пробы не заменяют аудит общего ядра, SIGKILL/OOM, публичной нагрузки или Vultr.

Непроверено: real VSI и repair quality, VM/HTTPS, независимый внешний пользователь, финальное видео, AP user study, многопользовательская нагрузка, полный screen-reader аудит и runtime reduced-motion preference (CSS/JS paths проверяются отдельно). Эти ограничения не скрываются passing tests.
