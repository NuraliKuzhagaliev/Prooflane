# Матрица требований и доказательств

Актуальная сверка после публичного релиза 6 ноября находится в [Agent Rush readiness](AGENT_RUSH_READINESS.md). Матрица ниже сохраняет результаты предыдущего локального прохода.

Снимок 2026-11-03. Scope: предлагаемый C1 CSV-аналитик. Идентификаторы правил и ссылки находятся в [RULES.md](RULES.md). Владение: `Owner` — основной инженер проекта; `User` — участник/администратор команды. Статусы обновлены по локальным тестам и артефактам 2026-11-03. Локальный PASS не означает PASS на Vultr.

`PASS` — проверка выполнена и доказательство сохранено; `FAIL` — проверка выявила дефект; `NOT_RUN` — ещё не выполнялась; `BLOCKED` — требуется недоступный внешний доступ. UNKNOWN описывает неизвестный факт, а не успешный gate.

## Обязательные gates

| ID | Правило | План реализации / действие | Приёмка и артефакт | Ответственный | Статус |
|---|---|---|---|---|---|
| G01 | T01 | Участник проверяет собственную допустимость | Подтверждение участника без сохранения ID-документов в репозитории | User | NOT_RUN |
| G02 | G01, E03 | Зарегистрировать команду допустимого состава | Проверить event dashboard и членство; аккаунтные действия выполняет участник | User | NOT_RUN — регистрация/купон сообщены пользователем; dashboard/состав команды не проверены |
| G03 | E02, R03 | Получить точный cutoff | Зафиксировать исходный timezone, UTC и Asia/Qyzylorda; submission form/официальный ответ | User | BLOCKED — cutoff UNKNOWN |
| G04 | T02 | MIT LICENSE, атрибуции зависимостей и происхождение данных | License inventory, история собственных изменений, только синтетический demo dataset | Owner | PASS для собственного MIT source + synthetic data; inventory THIRD_PARTY_LICENSES.md; не юридическая экспертиза |
| G05 | E04 | Развернуть control plane на Vultr VM | Deployment log, идентификатор инфраструктуры без секретов, anonymous browser smoke | Owner/User | BLOCKED — пользователь ещё не создал VM |
| G06 | E05 | Server-side Vultr provider adapter | Настоящий вызов с model ID, временем, успешным ответом; тесты с fixture отдельно | Owner/User | BLOCKED — VSI ещё не подключён; adapter/HTTP contract tests PASS |
| G07 | E06, E07 | Отдельный контейнер каждого задания; никакого host eval/exec | Runtime inspect и проба недоступности host-файлов; код и исполнение связаны run ID | Owner | PASS локальный Docker: sandbox-smoke.json, actual controls/no mounts; Vultr NOT_RUN |
| G08 | E08 | Передавать только входные данные; ключ хранить в control plane | Проверка состава env/mounts без вывода секретов; sandbox не видит credential canary | Owner | PASS локально: key variable отсутствует, env/mount injection отсутствует в коде; real-key run NOT_RUN |
| G09 | E09 | Timeout, memory, CPU и process caps | Реальные пробы превышения лимитов; exit reason и cleanup | Owner | PASS локальные caps inspect + timeout/output probes; OOM stress NOT_RUN |
| G10 | E10 | Cleanup в success/error/timeout ветках | После каждой пробы контейнер отсутствует; журнал жизненного цикла | Owner | PASS локальные cleanup/quarantine/regression; SIGKILL NOT_RUN |
| G11 | E11 | Вопрос → генерация → выполнение → проверка → объяснение | E2E с изменённым CSV, не только предзаполненным ответом; input/code/output hashes | Owner | BLOCKED для живой модели; reference/sandbox E2E + changed CSV PASS |
| G12 | E12 | Демонстрация блокируемого действия в sandbox | Видео реального run, видимые ограничения и продолжение полезной работы | Owner | NOT_RUN видео; настоящие локальные containment-пробы PASS |
| G13 | E13 | Объяснить границы компонентов и deployment в README | README соответствует реально развёрнутому build и указывает ограничения | Owner | PASS документация честно разделяет локальное и целевое Vultr deployment |
| G14 | R01 | Опубликовать подготовленный репозиторий | GitHub открывается без аккаунта; установка по README из чистой директории | Owner/User | BLOCKED — целевой remote не выбран |
| G15 | R01 | Дать судьям стабильный адрес | Внешняя проверка health + основной сценарий без API-ключа судьи | Owner/User | BLOCKED — deployment отсутствует |
| G16 | R01, S02 | Записать окончательный walkthrough | MP4/MOV metadata, размер, просмотр содержимого; прохождение G12 | Owner | NOT_RUN |
| G17 | R01 | Экспортировать слайды | Открытие PDF, проверка читаемости, соответствие функциональности | Owner | PASS draft6slides PDF/PPTX + rendered inspection; live evidence pending |
| G18 | E18, S02 | Подготовить cover | Проверить пропорции, читаемость и права на изображение | Owner | PASS cover1600x900 original layout + actual screenshot |
| G19 | S01 | Заполнить пакет описаний и tags | Подсчёт знаков + сверка с реальной формой; понятный сценарий и честные ограничения | Owner | DRAFT обновлён под сравнение двух версий; ограничения реальной формы и eligibility NOT_RUN |
| G20 | E14 | Завершить подачу участником | Подтверждение lablab submission и все ссылки; до G03 cutoff | User | BLOCKED — доступ/материалы не готовы |

## Продуктовая приёмка: внутренние решения, не новые правила конкурса

Эти пункты позволяют оценить выбранную реализацию. Они не утверждают, что конкурс требует конкретный framework, CSV-схему, сетевые флаги или формат журнала.

| ID | Наблюдаемое поведение | Проверка | Статус |
|---|---|---|---|
| P01 | Пользователь получает численный результат, исходные строки/колонки и выполненный код | Сравнить результат с независимо рассчитанной fixture; изменить входные значения | PASS — API smoke + browser changed CSV $0.60 |
| P02 | Ошибка вычисления видна; bounded retry имеет отдельные code/output records | Ошибочный первый код → корректировка → успешный run либо честная ошибка | PASS orchestration doubles + separate attempts; live repair NOT_RUN |
| P03 | Числа в объяснении соответствуют проверенному output | Автоматическая проверка provenance; неподтверждённое утверждение не маркируется verified | PASS — объяснение deterministic из проверенных чисел, не model narrative |
| P04 | UI показывает состояние настоящего backend | Пройти loading, success, error и отсутствие Inference/Docker; mock явно обозначен | PASS — browser loading/success/invalid CSV + VSI unavailable; Docker unavailable API test |
| P05 | Sandbox не имеет сети, прав host или пользовательского пути mount | Probe только на локальных синтетических целях; inspect запуска; без атаки сторонних ресурсов | PASS локальный Docker inspect/probes; universal escape resistance не заявлена |
| P06 | Повторяемый результат можно проверить после завершения задачи | Скачать receipt; проверить связи input/code/output, hashes и ограничения; hash не выдавать за независимую аттестацию | PASS — browser download + offline verifier; integrity без issuer authentication |
| P07 | Невалидные/слишком большие входы отвергаются до выполнения | Пустые, malformed и oversized CSV; traversal/HTML-like значения; содержимое рендерится как текст | PASS — malformed/oversize/Unicode tests + literal HTML-like browser text |
| P08 | Один run не раскрывает данные другого | Отдельные workspace/run IDs, управление доступом, ограничение concurrency | PASS — реальные HTTP cross-session checks + API tests |
| P09 | Основной путь доступен с клавиатуры и узкого экрана | Реальный browser, focus order, контраст, viewport; screenshot и trace | PASS проверенные viewport390/1440 и dialog Escape; full a11y NOT_RUN |
| P10 | Demo не требует приватных клиентских данных | Синтетический dataset, documented provenance, очистка содержимого и секретов из артефактов | PASS — authored synthetic examples, local secret-pattern scan |
| P11 | Одно изменённое допущение создаёт отдельный run в исходном режиме; original сохраняется | Actual HTTP/reference/Docker, source/hash/ownership, failed scenario и запрет цепочки baseline | PASS — artifacts/optimization/final/scenario-smoke.json, tests/test_comparison.py |
| P12 | Пакет двух версий проверяется без сервера | Оба receipt, lineage, полный source diff и все deltas; скрытая правка с пересчитанными hashes отвергается | PASS — независимые engineering/judge probes; authenticity/runtime truth вне scope |
| P13 | Редактирование CSV/context/mode не оставляет ложного текущего результата | Browser edit/reopen/history на desktop/mobile; ошибка600/601 | PASS — ux-cycle1.md; отдельный cycle2 также PASS для upload/recovery/comparison/history/mobile |

## Матрица оценки без вымышленных весов

Следующая таблица — наш план доказательств по E15, а не прогноз места. Баллы не присваиваются до проверки реализации. Шкала и веса конкретного события остаются UNKNOWN.

| Критерий E15 | Что показать судье | Доказательство | Риск недооценки |
|---|---|---|---|
| Application of Technology | Модель создаёт реально выполняемое вычисление; policy действует на runtime | G06–G12, P01–P06 | Fixture или локальный subprocess вместо настоящего provider/sandbox |
| Presentation | Один понятный вопрос и проверяемый ответ; сбой безопасно обработан | G16–G19, непрерывный walkthrough | Неподтверждённые рекламные claims, незаметная симуляция |
| Business Value | Конкретный аналитический job и измеряемое время до проверенного решения | User test с baseline; до измерения ценность — гипотеза | Придуманные часы экономии, отсутствие целевого пользователя |
| Originality | Связанные вычислительные доказательства и ясный containment момент | Сравнение конкретных workflows, P03/P06, данные по конкурентам | Утверждение уникальности без проверки альтернатив |

## Условия готовности

Submission-ready возможно только после PASS всех применимых G01–G20 и устранения критических defects. Локальные тесты могут закрывать P-пункты, но не подтверждают G05/G06/G14/G15/G20. Публичная ссылка, recorded video, живой Inference и deployed Vultr runtime должны проверяться отдельно. Optional Vultr Community публикация не входит в обязательные gates.
