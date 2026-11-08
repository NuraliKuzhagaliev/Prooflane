# Независимый финальный инженерный аудит — cycle 2

Дата: 2026-11-03. Проверенный backend commit: `4f8d1083b1686813415abcd9a71359a330398011`. Итог: **PASS в согласованной локальной области. Новых воспроизведённых дефектов не найдено; E1/E2/E3 остаются fixed_verified.** Облачная и пользовательская готовность этим не подтверждаются.

Это отдельный второй цикл после завершённого cycle1: заново прочитаны frozen backend, verifier CLI и текущая документация; создан новый репродуктор и новые синтетические БД; выполнены свежие пробы. Старый отчёт не скопирован как доказательство повторной проверки.

## Контракт и фактический срез

Read-only implementation review: scenario linkage, доступ и отказ, исправления E1/E2/E3, отсутствие host fallback, standalone проверка поддельных пакетов, точность финальных технических заявлений. UI/дизайн проверяются отдельно и сюда не входят. Backend соответствует указанному commit; документация и web на момент проверки ещё содержат изменения working tree. SHA-256 просмотренных backend/CLI/docs записаны в `engineering-cycle2-probes.json`, поэтому вывод относится к этому срезу, а не к будущим правкам.

Реальные права: workspace-write родителя и одобренное выполнение ограниченных локальных TestClient/CLI-проб; reviewer-role не создаёт дополнительную ОС-изоляцию. Изменялись только разрешённые cycle2-артефакты под `artifacts/optimization-review/`. Исходники, сервер PID43604, реальные runs/containers/quarantine, секреты и инфраструктура не изменялись. `.env` в probe не читается. Никакой установки, внешней сети, настоящего VSI или Docker-вызова моим репродуктором.

Команда: `$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe artifacts/optimization-review/engineering-cycle2-probe.py`. Артефакты: `engineering-cycle2-probe.py`, `engineering-cycle2-probes.json`, свежий `cycle2-original-packet.json` и три явно именованных `cycle2-forged-*.json`.

## Свежие результаты — 16/16 PASS

| Проверка | Наблюдение и предел |
|---|---|
| E1 — подтверждённо очищенный timeout | Два provider и два sandbox вызова, две сохранённые attempts, verified. Runtime/provider doubles, не качество ремонта настоящей модели. |
| E2 — choices=[null] | HTTP200 failed, sandbox_calls=0, failed-run виден в истории. Настоящий adapter с MockTransport. |
| E3 — lone surrogate в plan/model | Оба HTTP200 failed до sandbox; записи доступны в текущей сессии. Повторены исходные повреждённые payload. |
| Docker отсутствует | sandbox и vultr завершаются failed без summary/receipt; sandbox_calls=0 и provider_calls=0. Код source также не содержит пути запуска generated code на host. |
| Новый сценарий quantity 1→3 | Signed Decimal delta variance=2.00, billed=4.00, flagged_count=0; baseline байт-в-байт неизменён. |
| Lineage и права | Чужая сессия source/scenario/comparison→404; неправильный baseline hash→409; extra mode override→422; нет CSRF marker→403; scenario как parent→422. |
| Live gate и failed scenario | Без operator token→403. После synthetic cleanup=false ровно одна попытка, failed без summary, export→404, карантин активен, baseline неизменён. |
| Настоящий offline CLI | Reference/Docker пакеты родителя и новый reference packet: exit0; checker повторно вычисляет арифметику и отношения inputs без исполнения embedded code. |
| Поддельные пакеты с валидными individual receipts | Незаявленная notes-правка, дополнительная numeric-правка и ложная delta: individual receipts проходят собственную проверку, outer hash пересчитан, CLI всё равно даёт exit1 с конкретным semantic error. |

Негативные тесты CLI здесь проверяют содержательную связь двух входов. Отказ не вызван только старым hash: individual hashes/арифметика и bundle hash намеренно обновлены. У numeric подделки заявлен quantity change, дополнительно изменён unit_price той же строки; verifier обнаруживает незаявленное поле.

## Проверка артефактов и заявлений

Содержимое `artifacts/optimization/linux-final.txt` подтверждает 83 passing tests и одно предупреждение Starlette/httpx; Windows transcript также83, Node transcript6. Это просмотр реальных сохранённых логов, не самостоятельный повтор всего набора. `scenario-smoke.json` содержит36 проверок, пары reference/fixed Docker и ноль model calls; оба полных comparison packet дополнительно проверены моим CLI. Corpus report заявляет24/24 и no live AI; его исходные кейсы/ручные expectations относятся к фиксированной CSV-арифметике, не к модельной accuracy.

Свежий `sandbox-smoke.json` имеет время 18:28:48 UTC, scope REAL_LOCAL_DOCKER_NOT_VULTR. В CSV/timeout/output-cap результатах действительно присутствуют cleanup=true и inspected network=none; report содержит отдельный containment probe. Это сохранённые результаты предыдущего исполнителя, не утверждение, что reviewer заново запускал эти контейнеры.

Проверены текущие README, TESTING, FINAL_REPORT, SECURITY, ARCHITECTURE, SCENARIO_CONTRACT, TRY_PROJECT и технические утверждения DEMO/SUBMISSION. Существенных несоответствий проверенному backend не найдено:

- reference честно обозначен доверенной фиксированной арифметикой; sandbox — фиксированным рецептом без модели; VSI и VM остаются NOT_RUN.
- Одна numeric assumption, сохранённый оригинал, inherited mode, положительные variance без netting и signed deltas соответствуют реализации.
- Сравнение — гипотеза, не исправленный договор, fraud verdict или recovered savings.
- Hashes не заявлены подписью, runtime attestation или доказательством истинности CSV.
- In-memory quotas, один worker, Docker daemon/shared-kernel trust, 24h logical expiry без secure erase, синтетические данные и отсутствие human study явно указаны.
- Unit/API doubles, настоящие HTTP/Docker, browser и человеческая проверка не объединены в «accuracy». 83 tests не названы83 реальными контейнерами.

Сравнение CSV выполняется по нормализованным parsed cells; trim/quoting/newlines могут отличаться от исходных bytes. Формулировка «одно числовое допущение» корректна; обещания побайтовой идентичности CSV в проверенных ключевых документах нет. Доказательство технической корректности не устраняет открытую продуктовую гипотезу: fixed-schema арифметика сама по себе не требует AI.

## Остаточные ограничения

**NOT_RUN:** настоящий Vultr Inference и качество repair, VM/публичный HTTPS, cloud permissions/billing, внешний judge flow, нагрузка/аварийный SIGKILL/OOM, новые browser/a11y действия, финансовая или пользовательская оценка. **BLOCKED внешним доступом:** облачные gates остаются незакрытыми по состоянию проекта. Отсутствие найденных дефектов в этом срезе не является сертификацией безопасности Docker или доказательством отсутствия других ошибок.

Cycle2 не требует дополнительных исправлений в проверенной области. При последующих изменениях backend/provider/verifier необходимо оценить новый diff и повторить затронутые пробы; этот PASS нельзя автоматически переносить на другой код.
