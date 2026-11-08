# Независимый инженерный аудит — cycle 1

Дата: 2026-11-03. База commit `c2a3662`, проверены текущие изменения `comparison.py`, `app.py`, `provider.py`, CLI verifier и новые тесты. Первоначальный итог этого цикла был FAIL из-за medium E3. После исправления и независимого повторения исходного триггера итог: **PASS в проверенной области; E1/E2/E3 fixed_verified**. Это локальный контрактный review, не облачный release verdict и не второй финальный цикл.

## Область и доказательства

Исходники только читались. Разрешённые записи — этот отчёт и bounded probe-артефакты под `artifacts/optimization-review/`. Проверки работают с новыми синтетическими SQLite-каталогами и HTTP/Docker doubles; чтение `.env` подавлено. Фактические права прежние: workspace-write плюс одобренное выполнение локального TestClient; reviewer не получает отдельной ОС-песочницы. Текущий сервер 8765, реальные контейнеры, данные, карантин и секреты не затрагивались.

Репродуктор: `engineering-cycle1-probe.py`; вызов `.\.venv\Scripts\python.exe artifacts/optimization-review/engineering-cycle1-probe.py` с `PYTHONDONTWRITEBYTECODE=1`. Исходные результаты E1/E2 сохранены в `engineering-probes.json`, повтор — `engineering-cycle1-retests.json`. E3 до исправления и hashes файлов — `engineering-cycle1-found-probes.json`; повтор после исправления — `engineering-cycle1-probes.json`. Проверка написана независимо от production-тестов и вызывает настоящий API/adapter/verifier с подменёнными внешними зависимостями.

## E3 — medium / reliability / fixed_verified

**Место:** `prooflane/provider.py:73` — план проверяется только на тип и длину; `:75–77` — возвращённое имя модели только на тип и длину. API сериализует результат при `prooflane/app.py:382`.

**Триггер:** успешно прочитанный JSON провайдера содержит escaped lone surrogate `\ud800` в одном элементе plan или в returned model. Это допустимая для Python json.loads строка, но её нельзя сериализовать как UTF-8 response.

**Следствие:** адаптер принимает план, вызывается sandbox; результат записывается как verified, а HTTP-ответ завершается 500 при сериализации. На первом запросе клиент не получает session cookie, поэтому только что созданный run недоступен ему в истории; для существующей сессии чтение такого run также содержит проблемную строку. Это нарушение обработки повреждённого provider response, не обход арифметического verifier или изоляции кода.

**Доказательство до исправления:** cases `surrogate_plan` и `surrogate_model` в `engineering-cycle1-found-probes.json`: оба HTTP500, sandbox_calls=1. Дополнительно прямое чтение двух собственных синтетических БД показало `['verified']` в каждой; доступная через новую сессию история пустая. Первоначальный probe JSON фиксировал HTTP и счётчик, а проверка SQLite выполнена отдельно; репродуктор и JSON затем дополнены полем database_statuses. Реальных вызовов Vultr не было. Уверенность высокая.

**Минимальная коррекция:** перед возвратом плана проверить UTF-8-кодируемость каждого plan item и returned_model; некорректный Unicode преобразовать в ProviderError до sandbox.run. Код уже проверяется через `.encode()`; распространить ту же границу на оставшиеся строки ответа.

**Acceptance:** оба исходных payload дают управляемый failed-run с HTTP200 согласно текущему контракту API, sandbox_calls=0, summary/receipt отсутствуют, запись видна в текущей сессии. Валидные Unicode строки продолжают работать. Добавить проверки адаптера и хотя бы один путь через API, поскольку исходное падение происходило после расчёта при сериализации ответа.

**Независимый retest:** после добавленного UTF-8 encode plan/model оба исходных cases дают HTTP200, sandbox_calls=0, stored_statuses/database_statuses=[failed]. Ошибка отклоняется до исполнения. Исходное воспроизведение E1/E2 и adversarial linkage cases в повторе остаются PASS. Реализация поправлена родителем, reviewer исходники не менял.

## Исправления и adversarial проверки

- **E1 fixed_verified / PASS:** прежний чистый timeout с cleanup=true теперь приводит к двум provider/sandbox вызовам и verified; обе попытки сохранены. cleanup=false и неизвестный cleanup в scenario не повторяются, failed-сценарий не экспортируется, baseline неизменён.
- **E2 fixed_verified / PASS:** choices=[null]/[строка] теперь дают ProviderError; через API HTTP200 failed и одна сохранённая запись, без неперехваченного 500.
- **PASS:** валидный bundle независимо пересчитан, signed delta `-2.00`, billed delta `0.00`.
- **PASS:** новая корректно пересчитанная individual receipt с незаявленным изменением notes, vendor той же строки, цены другой строки, даже числового форматирования `6→6.0`, либо удалением строки отклоняется как undeclared change. Это проверка отношений inputs, а не только старого hash.
- **PASS:** изменение parent hash, исходного before-value, режима и сравниваемой delta с пересчётом individual/bundle hashes отклоняется соответствующим semantic check.
- **PASS:** чужая сессия получает404 для создания сценария; отсутствующий live operator token получает403; failed scenario сохраняет baseline байт-в-байт и comparison endpoint даёт404.
- **PASS:** прежний глубоко вложенный stdout и нормальный контроль продолжают корректно возвращать failed/verified соответственно.

## Оценка реализации и границы

Новое API поддерживает ровно одну числовую правку, что соответствует уточнённому `SCENARIO_CONTRACT.md`. Сценарий наследует режим и идёт через общую функцию исполнения/квоты; исходный receipt не изменяется. Standalone bundle содержит оба inputs и проверяется без SQLite/сети. Сравнение проверяет все нормализованные CSV cells, а не только суммарные деньги; нечисловые изменения не теряются. Изменения пробелов, CSV quoting и line endings нормализуются существующим parse_csv — это следует описывать как один изменённый числовой assumption, а не обещать побайтовую идентичность остальных исходных CSV bytes.

Новые `tests/test_comparison.py` и retry/provider tests явно используют doubles/reference arithmetic. Они подтверждают API и контракты, но не качество генерации модели или реальную облачную изоляцию. Заявленные родителем 80 passing pytest не подменяют мои независимые пробы; полный набор в этом цикле повторно не запускался. UI сейчас меняется другим worker и исключён из этой проверки.

Дополнительно независимо прочитаны `artifacts/optimization/scenario-smoke.json` и полные reference/sandbox comparison bundles, затем оба bundle пропущены через настоящий check_bundle: PASS, delta=-320.00/0.00. Sandbox bundle содержит разные container IDs, cleanup=true и inspected network=none/read-only/uid65534/memory/cpu/PID/capdrop/host_mount_count=0 для обоих runs; reference runtime обозначен trusted-reference. Это проверка содержания ранее полученных реальных локальных артефактов, не новый Docker-прогон reviewer.

**NOT_RUN мной:** реальный VSI, deploy на Vultr VM, самостоятельный Docker-прогон новых сценариев, браузер, нагрузочные/аварийные тесты. Неаутентифицированные receipts и in-memory quota остаются ранее описанными ограничениями; новый код не делает их подписью или долговечным бюджетным контролем.
