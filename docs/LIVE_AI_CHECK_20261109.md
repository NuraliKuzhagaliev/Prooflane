# Живой AI через браузер, 9 ноября 2026

**PASS для полного проверенного сценария:** публичная форма Prooflane → Vultr Serverless Inference → сгенерированный Python → настоящий Docker → независимый Decimal-verifier → объяснение Vultr → скачанный JSON-пакет → офлайн и браузерная проверка. Использованы только вымышленные invoices/contracts.

Локальное время успешного baseline: 9 ноября около00:14, Asia/Qyzylorda. Timestamp API: `2026-11-08T19:14:24.341640+00:00`.

## Наблюдаемый результат

| Поле | Значение |
|---|---|
| Публичный адрес | https://45.76.92.198/ |
| Mode | `vultr`, показан в интерфейсе как Vultr agent |
| Requested/returned model | `deepseek-v4.1-flash-1017` |
| Case ID | `f73c5d8c-8923-40e2-b070-5123983a5063` |
| Run ID | `93ccc09e-5289-402d-b7b8-41be8c8e958e` |
| Generation request ID | `chatcmpl-da46cfa5-ca31-4ac1-8e13-9757e978f989` |
| Explanation request ID | `chatcmpl-de6f9e21-11e9-41a9-a13b-0f4ad4b2af72` |
| Успешный прогон | 2 модельных вызова, 1 генерация без correction |
| Usage из ответов | Генерация909 total tokens, объяснение116 total tokens |
| Охват | 7из8 строк, C2R выбран явно, INV506 исключён с причиной |
| Billed / positive variance | USD7110.00 / USD768.00 |
| Положительные отклонения | 5из7 включённых строк |
| Runtime | Docker, exit0, cleanup=true |
| Время самого контейнера | 723.04мс; это не полная задержка AI-запроса |
| Контейнер | `85a151c376c2b43c982a10debb82cb17b5f6672da01cc086bc09e25ccd48cf8c` |
| Наблюдавшиеся ограничения | network none, non-root65534, read-only root, host mounts0, memory128MiB, cpu0.5, pids32 |
| Офлайн пакет | 7групп PASS |
| Браузерный загрузчик пакета | 7групп PASS |
| Reload | То же дело и Vultr agent восстановлены, нового исполнения не было |

[Сырой отчёт](../artifacts/live-ai-20261109/live-evidence.json) · [Скачанный из браузера пакет](../artifacts/live-ai-20261109/live-case-packet.json) · [Браузерная проверка](../artifacts/live-ai-20261109/browser-checks.json) · [Ledger](../artifacts/live-ai-20261109/live-ledger.jpg) · [Proof с обоими ID Vultr](../artifacts/live-ai-20261109/live-proof.jpg).

## Найденный сбой и исправление

Первый фактический браузерный запуск завершился `Vultr model output was incomplete`. Приложение остановилось до Docker, не создало case и не выдало непроверенную сумму. [Диагностика](../artifacts/live-ai-20261109/initial-failure.json) и [кадр](../artifacts/live-ai-20261109/initial-failure.jpg) сохранены. В этой старой записи точный finish_reason и usage не сохранены; утверждать, сколько именно токенов ушло на reasoning, нельзя.

По [официальной документации Vultr](https://api.vultrinference.com/docs/concepts/reasoning) модель может расходовать reasoning и финальный ответ из общего completion-лимита. Для текущего семейства DeepSeek V4.1 адаптер теперь явно передаёт `reasoning.effort=none` для ограниченных JSON-задач генерации и выбора объяснения. Другие model profiles не менялись; caps4096/1024 не повышены. Это устраняет зависимость от дефолтного thinking-режима; точная причина конкретного первого обрыва не доказана без его полного envelope. [Контракт API](https://api.vultrinference.com/docs/reference/create-chat-completion).

Незавершённые ответы по-прежнему отвергаются. Для известных finish_reason в сообщении теперь сохраняется безопасная причина. Форма показывает `failed_run.error` рядом с общим отказом baseline и очищает поле operator token. Автоматического повторного модельного запроса не добавлялось. Повтор после исправления был отдельным намеренным запуском через ту же публичную форму.

В этом цикле было два пользовательских запуска: один незавершённый запрос генерации и успешный прогон с двумя вызовами. Usage неуспешного запроса неизвестен; полная стоимость не измерялась. Никаких альтернативных моделей или Reference-fallback не использовано.

## Код, развёртывание и проверки

- Изменены `prooflane/provider.py` и `web/workbench.js`; добавлены regression-тесты provider-профиля, отказа на length и вывода failed-run диагностики с очисткой credential.
- **179 Python PASS**, одно существующее предупреждение Starlette; **26 JavaScript PASS**. [Python](../artifacts/live-ai-20261109/pytest.txt) · [JavaScript](../artifacts/live-ai-20261109/node-tests.txt).
- Два файла опубликованы с проверкой SHA-256 `d0d13f8cf7707081592fdbf78d4606cb7b9a14c6573994a8ad598d0b60d9025d`. [Manifest](../artifacts/live-ai-20261109/release-manifest.json). Rollback: `/opt/prooflane/rollback/pre-live-fix-20261108T191326Z.tar.gz`.
- `.venv/Scripts/python.exe scripts/verify_receipt.py artifacts/live-ai-20261109/live-case-packet.json` → passed=true,7групп. Скрипт не исполнял код из пакета.
- API-ключ Vultr не переносился с VM. Первоначальный перенос operator token был отклонён автоматической проверкой разрешений; после явного согласия пользователя токен использован в password-поле только своего HTTPS-сайта. Временный локальный файл удалён сразу после ввода, поле очищено после запроса; секретные значения в evidence не записывались.

Проверка подтверждает этот вымышленный сценарий и текущую модель. Она не гарантирует доступность провайдера, корректность любого будущего сгенерированного кода, подлинность договоров или прохождение конкурсной подачи. Другие новые платные прогоны не выполнялись.
