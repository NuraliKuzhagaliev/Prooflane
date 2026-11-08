# Независимый ограниченный аудит Prooflane

Дата: 2026-11-03. Объект: текущее рабочее дерево D:/projects/vultre, prooflane/*.py, sandbox/runner.py, web/app.js, tests и artifacts/sandbox-smoke.json. Ревизия Git не задана. Аудитор не менял implementation, не вызывал Vultr и не использовал настоящие секреты.

Разрешения: фактическая среда workspace-write; безопасные API-пробы выполнены с require_escalated из-за блокировки asyncio socketpair внутри Windows AppContainer. Данные проб находятся только в .cache/audit. Это независимый контекст ревью, не отдельная OS-песочница.

## F1 — HIGH / P1: сбой очистки не останавливает новые sandbox-запуски

- Место: prooflane/sandbox.py, финальный блок run() после _cleanup; prooflane/app.py:228–234.
- Триггер: Docker завершает/теряет связь во время удаления, _cleanup возвращает False. run() сообщает Stop further runs, но не хранит запрет; API освобождает semaphore.
- Последствие: когда daemon снова отвечает, следующий запрос открывает новый контейнер без проверки оставшегося старого. При неподтверждённой очистке исполнявшийся процесс может остаться активным, а новые запуски накапливать контейнеры. Гарантия lifecycle/time caps в этой ветке не обеспечена.
- Воспроизведение: .venv/Scripts/python.exe .cache/audit/reproduce.py. Test double первого run выбрасывает SandboxError с cleanup=False; второй возвращает корректный результат. Наблюдение: first_status=failed, second_status=verified, sandbox_calls=2.
- Статус: FAIL, open. Уверенность высокая; поведение API воспроизведено, искусственный сбой Docker daemon не производился.
- Минимальное исправление: quarantine/latch после неподтверждённой cleanup, отказ новых code/probe вызовов до подтверждённого удаления принадлежащих приложению контейнеров. На старте проверять stale контейнеры по собственному label; не затрагивать чужие контейнеры. Сброс запрета только после положительного доказательства отсутствия.
- Приёмка: cleanup=False → следующий API code/probe запрос не вызывает Docker execution; recovery с подтверждённым отсутствием восстанавливает работу; startup со stale собственным контейнером закрывает gate.

## F2 — MEDIUM / P2: некорректный Unicode CSV вызывает HTTP 500

- Место: prooflane/analysis.py:29, text.encode('utf-8') до обработчика ошибок.
- Триггер: JSON содержит lone surrogate в csv (например добавленное \ud800).
- Последствие: UnicodeEncodeError выходит из InputError boundary; UI получает внутреннюю ошибку вместо понятного отказа на неверный CSV. Код не исполняется.
- Воспроизведение: тот же reproduce.py, invalid_unicode_csv.http_status=500.
- Статус: FAIL, open. Уверенность высокая.
- Исправление: проверять UTF-8-кодируемость в try/except UnicodeError и преобразовывать в InputError; проверить также question/filename перед сохранением/вызовом модели.
- Приёмка: escaped surrogate CSV → HTTP422; обычная кириллица/emoji в текстовых ячейках продолжают работать.

## F3 — MEDIUM / P2: Unicode operator_token вызывает HTTP 500

- Место: prooflane/app.py:158, secrets.compare_digest(str,str).
- Триггер: live явно включён и настроен, клиент передаёт неASCII token. Реальный ключ в пробе не нужен: injected provider + test-only env.
- Последствие: compare_digest выбрасывает TypeError; неправильный token приводит к внутренней ошибке вместо отказа403. Авторизация не обходится и provider не вызывается.
- Воспроизведение: reproduce.py, unicode_operator_token.http_status=500.
- Статус: FAIL, open. Уверенность высокая.
- Исправление: сравнение UTF-8 bytes с корректной обработкой surrogate либо ASCII-валидация operator_token и конфигурации. Не возвращать token в ошибках.
- Приёмка: любой неправильный Unicode token →403/422 без обращения к provider.

## Наблюдение: срок видимости не является гарантией удаления

prooflane/store.py удаляет записи старше24h только при следующем add. get/list скрывают их сразу по возрасту, но на простаивающем сервере строка остаётся в SQLite. Проба: api_visible=false, database_rows=1. Пока нет явного обещания удаления через24h, это ограничение, а не подтверждённый privacy-дефект. Документировать lazy retention или реализовать периодический purge. SQL DELETE также сам по себе не доказывает физическое стирание страниц/бэкапов.

## Что подтверждено

- PASS (inspection): generated code исполняется только в sandbox/runner.py внутри Docker; API не передаёт shell-команды/host mounts или секретные env в контейнер.
- PASS (inspection + raw artifact): artifacts/sandbox-smoke.json содержит реальные container/image IDs, observed HostConfig, результаты timeout/output caps/cleanup, сеть none, UID65534, memory128MiB, CPU0.5, PID32. Проверены содержимое и границы формулировок, не только итоговый флаг.
- PASS (inspection): CSV/модельные строки выводятся через textContent; Live требует явного enable и operator token; provider использует фиксированный HTTPS endpoint без redirect и не отправляет csv payload.
- PASS (inspection): receipt-проверка пересчитывает hashes и фиксированную арифметику; явно не удостоверяет автора/реальность runtime.
- NOT_RUN: живой Vultr Inference, развёртывание/HTTPS, multiworker нагрузка, атаки на ядро/container runtime, полный браузерный UX, физическое удаление данных. Аудит не является сертификацией безопасности.

## Повторная проверка после исправлений основным агентом

Основной агент изменил implementation во время аудита. Исходное наблюдение сохранено в reproduction-before.json. Повтор той же команды завершился exit0; новый reproduction.json содержит:

- F1: first_status=failed, second_status=failed, sandbox_calls=1. API прекращает execution после cleanup=False; inspection подтверждает persistent sandbox-quarantine.json и загрузку quarantine при создании приложения. **fixed_verified** для воспроизведённой ветки.
- F2: invalid_unicode_csv.http_status=422. **fixed_verified**.
- F3: unicode_operator_token.http_status=403, provider не вызван. **fixed_verified**.
- Retention: api_visible=false, database_rows=0 после get; очистка теперь при чтении и записи. Простой без запросов и физическое стирание всё ещё не проверены и не гарантируются этой пробой.

Остаточная проверка, NOT_RUN: аварийное завершение процесса между созданием контейнера и записью quarantine-маркера. Стартап-проверка stale контейнеров с собственным label полезна для этой отдельной ветки; в данном аудите процесс и daemon намеренно не прерывались.

Артефакты: reproduce.py, reproduction-before.json и reproduction.json в этой директории. Ни один найденный дефект аудитором не исправлялся. Статусы open выше описывают исходный снимок; итоговые статусы определены этим разделом.
