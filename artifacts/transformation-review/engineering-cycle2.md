# Независимый engineering review — cycle 2

Дата: 2026-11-04, Asia/Qyzylorda. Рецензент: `v3_engineer` / `hub_evidence_reviewer`.

**Итог:** второй цикл обнаружил новую P2 гонку чтения CSV. Root исправил её; независимый повтор подтверждает сохранение последнего выбора источника и отмену устаревших чтений. Остальные четыре исправления cycle1 сохранились. Backend probe: **50/50 PASS**, из них21 новых граничных проверок. Node source-function probe: **12/12 групп PASS**. В этом ограниченном scope открытых воспроизведённых P1/P2 после исправления не осталось.

## Проверяемая ревизия и полномочия

Начальный target — `bd25e99cf08dd25a0a49665dc0713ccf8d3b54e0`, backend checkpoint `b1bd9a4`. После воспроизведения новой ошибки проверена рабочая правка `web/workbench.js` с SHA-256 `50938a0ad336acd5cc9d86dac7d368219f8615f13a1ccd4acc840c4243d36552`. Этот hash включает параллельную mobile chart правку автора; Node probe проверяет исполняемые state functions, а не визуальную часть chart.

Прочитаны AGENTS.md и текущие API/state/verification участки. Рецензент изменил только собственные probes и этот отчёт. Реализация, настройки, пакеты и работающий localhost server не изменялись. Browser оставлен отдельному design reviewer. Использованы унаследованные Windows workspace-write permissions; TestClient — точечно разрешённый локальный процесс с временной БД внутри review directory. Отдельной OS sandbox рецензента нет. Внешние сервисы, платежи и реальные model calls не выполнялись.

## E5 — новая ошибка, найденная вторым циклом

**Severity P2; confidence high.** `web/workbench.js:108` (`loadSource`; на исходной ревизии строка104).

Trigger: выбрать первый файл, пока `file.text()` ещё ожидается, выбрать второй; второе чтение завершается раньше первого. Исходный code применял результаты обоих чтений без идентификатора запроса. Последний callback перезаписывал textarea и filename label первым, уже устаревшим файлом. Та же ветка могла перезаписать более новую вставку текста или вновь открытый draft. Следствие — пользователь анализирует не последний выбранный источник.

**Воспроизведение на исходном SHA `42428edbaedae8f9029cbfdb97839f2d529ba8ab0e1306b87a859f02a54ba65d`:** настоящая функция `loadSource` исполнена в Node VM с двумя отложенными `file.text()` Promise. Последний выбранный файл `second.csv`, но после обратного порядка завершения `final_text = "first stale source"`, `final_label = "first.csv · 100 bytes"`. Это воспроизведение source function с контролируемой I/O boundary, не имитация результата браузерного клика.

**Минимальное исправление:** независимый token чтения для каждого source; invalidation при новом выборе, paste, reset, sample и открытии дела; проверка token после await, в error и finally; сохранение loading флага нового чтения; запрет match/create, пока любой источник читается. Реализацию выполнил root.

Повтор на итоговом hash:

| Проверка | Наблюдаемый результат |
|---|---|
| Первый файл завершается после второго | `second selected source`, label `second.csv`; последний выбор сохранён |
| Устаревшее чтение завершается, пока новое ещё pending | Новый loading остаётся true; после нового чтения false |
| Invoice и contract читаются параллельно | Оба результата сохранены независимо; все loading false после завершения |
| Match/create при pending втором источнике | **0 POST requests** |
| Pending file → paste | Более новый pasted source сохранён |
| Pending file → reset | Пустой новый draft сохранён |
| Pending file → sample | Sample invoices сохранены |
| Pending file → openCase | Старое чтение отменено; source не записан в новый контекст |

**E5 CLOSED после независимого повтора.** Четыре cycle1 дефекта также повторены: failed alternative сохраняет draft при0/1 предыдущем варианте; source-fetch failure не меняет case identity; string checklist показывает успешные именованные checks; stale packet response остаётся скрытым, inputs заблокированы во время проверки.

## Новые backend boundaries

В дополнение к29 cycle1 проверкам добавлен отдельный маленький manual oracle:

- Два invoice records с quantity2/3, price10/7 и общим contract8: billed41, positive variance4. Контракт включает обе крайние даты интервала. Contract target9 даёт2; range0..12 даёт совместные границы0..41.
- UTF-8 BOM, CRLF, quoted multiline invoice ID, quoted vendor, emoji и literal `<script>` в notes корректно нормализованы. Shared contract ID содержит `/`, `<script>`, `&`, newline и Unicode. Это данные, не URL path. Оба нормализованных records2/3 сохраняют правильные source links; raw source bytes точно сохранены в packet. Прохождение backend не доказывает browser XSS safety.
- Bounds update сохраняет case/baseline IDs и повышает revision1→2. Попытка variant с revision1 даёт409 **до появления нового run**; bool revision даёт422. Валидная повторная попытка даёт revision3 и ровно один новый вариант.
- Surrogate, NUL и exponent notation в range input дают422, без500. Они не преобразуются в разрешённую цену. Case label с CRLF не попадает в `Content-Disposition`: filename формируется из case UUID.
- Отдельная временная session: создание дела и119 чередующихся GET case/packet проходят; операция121 даёт429. Packet GET и POST bounds используют тот же исчерпанный quota. Другая session на том же IP, пока общий IP cap не исчерпан, продолжает работать. Эти проверки не потребляли квоту пользовательского localhost сервера.

Полный independent probe: **50/50 PASS, exit0**, один известный Starlette TestClient deprecation warning. Включает повтор ownership, provider gating через doubles, expiry и rehashed source/analysis/context attacks из первого цикла.

## Реальные сохранённые артефакты

Повторно прочитаны обновлённые после server restart packets, а не старые IDs из cycle1:

| Packet | Case / created UTC | SHA-256 файла |
|---|---|---|
| `artifacts/transformation/reference-case.json` | `054c16d1-1d74-4919-ab3e-738f8dde1f91`, `2026-11-03T19:19:16.354897+00:00` | `ec68ea9dccfe77c523880c9e8036f007ff7b99731a018187f688ef673af6757b` |
| `artifacts/transformation/sandbox-case.json` | `14d59427-54c0-4b42-803b-3fd7919420d9`, `2026-11-03T19:19:19.346672+00:00` | `905343f267d8ebff91e1f797a195964053ef57eb853b5d44b7e1b2c1dd9281f7` |

Оба независимо пересчитаны: baseline768, alternatives368/568, coverage7/8 с исключением, bounds148..1193, model calls0. Это проверка raw content и арифметики уже записанных настоящих HTTP/Docker артефактов. Рецензент не выдаёт её за новое исполнение контейнеров или runtime attestation.

## Воспроизведение

```powershell
git rev-parse HEAD
.venv/Scripts/python.exe artifacts/transformation-review/principal-backend-probe.py
node artifacts/transformation-review/principal-ui-probe.mjs
```

Python probe использует реальные application routes через TestClient с изолированными temporary databases. Provider/runtime doubles явно помечены; новых real model calls нет. Он содержит assertions и завершает процесс ошибкой при неудаче. Node probe извлекает текущие функции из исходника, подменяет только DOM/render/transport boundaries, проверяет12 групп и возвращает exit1 при нарушении. До исправления E5 его диагностический вывод показывал старый файл; после расширения assertions общий результат `passed:true`.

Срез backend неизменён:

| Файл | SHA-256 |
|---|---|
| prooflane/case_api.py | `e866a39fda8d5d3af7401b7c3b051d4be57504390824d7758c16927d75be4485` |
| prooflane/case_evidence.py | `91f8bc3dec194bcb9b4f9cc2feae11d0d68b7c2b47380f35575c358d4b56aa93` |
| prooflane/app.py | `ff31f7a3085dd3cbb382ee1486332f4d79c07954990893c59036cd6b7ae9f958` |
| prooflane/reconciliation.py | `e1ed253e77e85e89d92bace19d8a5843546b9edb52b6d68633296dbc80cd5b5c` |
| prooflane/intelligence.py | `b793ccd575c89e9f047dc4594314fb0d343baf45577f8d18b15c83ccb0cee14d` |

## Ограничения заключения

**NOT_RUN этим reviewer:** реальный browser workflow, mobile layout, focus/accessibility, Vultr VM/HTTPS/VSI, multiworker operation, distributed-load resistance, crash/OOM experiments, пользовательская оценка пользы. Самостоятельная math oracle относится к отдельному scientist review. Backend normalization и Node state probes не заменяют эти виды доказательств.

Заключение относится к проверенным hashes и bounded scenarios. Оно не означает отсутствие всех ошибок или готовность конкурсной облачной части.
