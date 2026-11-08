# Независимый engineering review — cycle 1

Дата: 2026-11-04, Asia/Qyzylorda. Рецензент: `v3_engineer`, роль `hub_evidence_reviewer`.

**Итог:** четыре ошибки клиентского состояния найдены и исправлены исполнителем в ходе review. Повтор исполняемых функций подтверждает исправления. В проверенной области backend новых дефектов после исправления baseline context не найдено. Это разрешает следующий локальный verification cycle, но не подтверждает браузерный путь или готовность Vultr.

## Контракт и фактические границы

- Target: commit `9b5bc30786cb21b7c86bff25c622a7d0b09d7c2d` плюс текущие изменения `case_evidence.py`, GET quotas и frontend. Прочитаны AGENTS.md и WORKBENCH_CONTRACT.md; вложенных AGENTS.md не найдено.
- Проверяются: session ownership, original/alternative identity, source decisions, joint inputs, packet reconstruction, mode/live gates, expiry, асинхронное состояние интерфейса. Сначала прочитаны реальные packets и исходники, затем связанные тесты; выводы автора не использовались как доказательство PASS.
- Разрешены read-only source/artifact inspection, offline CLI, собственные локальные probes с временной БД и явно обозначенными doubles. Записаны только этот review и два воспроизводимых review scripts. Реализация не редактировалась, packages не устанавливались, сервер не перезапускался.
- Реальные permissions унаследованы от родителя: Windows workspace-write и restricted network, не отдельная OS-песочница рецензента. TestClient probe исполнен с точечной `require_escalated` для локального runtime. Отклонений автоматического review не было. Live provider, VM, публикация и отправка сообщений внешним адресатам исключены.

## Исправленные дефекты

| ID / severity | Trigger → consequence | Evidence / confidence | Минимальное исправление и повтор |
|---|---|---|---|
| E1, **P2** | Sandbox альтернативы становится недоступен. API возвращает HTTP200 `{case: unchanged, failed_run}`. Старый `mutateCase` считал это успехом; `runAlternative` очищал draft и либо обращался к отсутствующему последнему варианту, либо называл неудачный новый вариант сохранённым по состоянию предыдущего | Исходный контроль потока `web/workbench.js:286` / вызывающий `runAlternative`; backend shape подтверждён отдельным QA test и прочитанным API. Высокая уверенность. До исправления обнаружено статически; первый исполняемый probe уже увидел исправление | Проверять `result.failed_run` до `acceptCase`, показывать failure и возвращать false, сохраняя draft. Собственный Node probe: 0 и 1 предыдущий вариант → draft сохранён, error показан, success notice отсутствует, exception отсутствует. **PASS после fix** |
| E2, **P2** | Валидный case packet возвращает `checks: string[]`, но старый `checksList` читал поля object и выводил шесть `Check · not passed` под успешным общим статусом | Реальный JSON checker + `web/workbench.js:396`; высокая уверенность. До fix — прямое несоответствие типов | Нормализовать string checks с успешностью результата. Вызов из `verifyPacket` передаёт `result.passed === true`; собственный probe выводит именованные строки `passed`. **PASS после fix** |
| E3, **P2** | При открытии другого дела вторичный `/source` fetch падает. Старый `acceptCase` заранее менял active case, оставляя старые строки и визуальное состояние; последующее действие могло адресовать другое дело | Прочитан порядок присваивания до await в `web/workbench.js:169`; высокая уверенность. Исполнитель исправил до первого probe | Сначала получить source, затем атомарно сменить active и rows. Probe с отказом fetch сохраняет `old-case` и `old-invoice`. **PASS после fix** |
| E4, **P2** | Пользователь изменяет JSON/file, пока сервер проверяет предыдущий packet. Старый поздний ответ показывал `Packet checks passed` для уже изменённого содержимого | **Воспроизведено исполнением настоящей `verifyPacket`** с отложенным transport: на SHA `fe5a770bbf8587e2de47c8a17191a5c2f27d0931a0ce443e0025d6a41cfebe99` текущий текст `{"tampered":true}`, результат visible=true, badge=`Packet checks passed`, editor disabled=false. Это source-function VM probe, не browser | `web/workbench.js:412` фиксирует packetRequest; строка418 отбрасывает старый ответ; editor/file также отключены во время запроса. Тот же probe на SHA `f12a0d53e0d500c4e65be5e1bb3d82b0e95da07a8e45432594da010deb2f795d`: result visible=false, editor disabled=true. **PASS после fix** |

Здесь нет утверждения, что первые три ошибки были нажатием воспроизведены в браузере до исправлений. Они установлены по согласованным backend responses и исходному control flow, а исправления проверены выполнением функций.

## Выполненные независимые проверки

```powershell
.venv/Scripts/python.exe scripts/verify_receipt.py artifacts/transformation/reference-case.json
.venv/Scripts/python.exe scripts/verify_receipt.py artifacts/transformation/sandbox-case.json
.venv/Scripts/python.exe artifacts/transformation-review/principal-backend-probe.py
node artifacts/transformation-review/principal-ui-probe.mjs
```

Обе CLI проверки — **PASS**, source coverage 7 из8, один явно исключённый источник, 2 alternatives, range148.00..1193.00. Прочитаны raw source decisions, baseline/alternative totals и runtime provenance: reference/sandbox, по нулю model calls, у трёх Docker receipts cleanup=true. Это повторная проверка сохранённых реальных HTTP артефактов, не повторное физическое выполнение контейнеров этим рецензентом. Hash и receipt не являются runtime attestation.

Собственный backend probe — **29/29 PASS**:

- Manual totals768.00 →368.00/568.00 и source coverage подтверждены на обоих сохранённых packets.
- Изменение договорного source, range result или baseline case context с пересчитанным root hash отвергается. В context attack пересчитан и receipt hash.
- Foreign session: чтение дела, packet, source и mutation дают404.
- В локальном TestClient с **provider/runtime doubles**: wrong operator token403; выключение live gate после baseline503; ни дополнительных generation/execution, ни изменений дела; extra mode injection422.
- Escaped invalid Unicode input422, malformed UTF-8 verification body200/`passed:false`; expiry baseline делает case404 и убирает его из списка.
- Настоящая VSI не вызывалась. Mode label `vultr` в probe обозначает только тест gating с doubles, не live evidence.

Node probe исполняет извлечённые функции текущего `web/workbench.js` в VM. DOM и transport boundaries заменены небольшими doubles. Проверены обе failure ветви, atomic accept, string checklist и stale packet response. **Это не end-to-end browser verification.**

Первый backend probe завершился ошибкой удаления собственной временной SQLite БД после проверок из-за удержанного probe connection. Добавлено явное закрытие этого соединения и сборка недостижимых connections; повтор завершился exit0. Остаточная временная папка удалена только после проверки её точного абсолютного пути внутри review directory. Это дефект тестового probe, не заявленный дефект продукта.

## Срез файлов после повторов

| Файл | SHA-256 |
|---|---|
| prooflane/case_api.py | `e866a39fda8d5d3af7401b7c3b051d4be57504390824d7758c16927d75be4485` |
| prooflane/case_evidence.py | `91f8bc3dec194bcb9b4f9cc2feae11d0d68b7c2b47380f35575c358d4b56aa93` |
| prooflane/case_store.py | `3a3250189cf919862d89b2e2ed15c8a048671d96df030c3e98ee26d43db00933` |
| prooflane/reconciliation.py | `e1ed253e77e85e89d92bace19d8a5843546b9edb52b6d68633296dbc80cd5b5c` |
| prooflane/intelligence.py | `b793ccd575c89e9f047dc4594314fb0d343baf45577f8d18b15c83ccb0cee14d` |
| web/workbench.js | `f12a0d53e0d500c4e65be5e1bb3d82b0e95da07a8e45432594da010deb2f795d` |

## Остаточные границы

- **NOT_RUN:** новый UI в настоящем браузере этим рецензентом; full accessibility/keyboard/focus audit; live VSI, Vultr VM, внешний walkthrough и нагрузочная эксплуатация.
- **NOT_RUN:** multi-process concurrency. Реализация прямо рассчитана на один worker: in-process mutation lock + SQLite optimistic revision. Это ограничение, не скрытая поддержка multiworker.
- Range/priority mathematics подробно не переаудирована здесь: отдельный scientist выполняет независимый oracle. Этот reviewer проверил целостность передаваемых результатов и отрицательные контроли.
- GET case/packet теперь используют общий case quota; его наличие проверено в коде. Throughput, event-loop latency и защита от распределённой нагрузки не измерялись.
- Public source text выводится через `textContent`/создание DOM nodes, IDs в URL проходят encodeURIComponent. Новых прямых HTML injection sinks при этом read-only просмотре не найдено; полноценный XSS fuzzing **NOT_RUN**.

Новых незакрытых воспроизведённых P1/P2 в этом bounded review после исправлений не осталось. Следующий цикл должен проверить frozen revision и настоящую браузерную интеграцию, а не считать эти Node probes её заменой.
