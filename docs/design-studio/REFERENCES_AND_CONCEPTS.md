# Prooflane: исследование арт-дирекции и три разные концепции

Дата просмотра: 5 ноября 2026, Asia/Qyzylorda. Роль: Creative Director / Visual Designer. Этот документ и векторные эскизы — проектирование, не browser verification готового продукта. Исходники приложения не изменялись. Другие проекты пользователя не сравнивались: AGENTS ограничивает работу текущим проектом и запрещает изменение соседних; для этого аудита достаточно двух предыдущих версий Prooflane и их сохранённых кадров.

## Почему возник цикл шаблонов

Прочитаны AGENTS.md, web/index.html, web/workbench.css, docs/WORKSPACE_DESIGN.md и новый запрос. Наблюдаемая структура текущего приложения: постоянная левая навигация, повторная навигация вкладками, заголовок дела, набор одинаковых ограниченных панелей, числовые блоки, таблица с инспектором в ещё одной панели. История и runtime занимают тот же визуальный статус, что основные действия. Смена кремовой hero-композиции на синий dashboard изменила поверхность, но снова сделала контейнер основной единицей проектирования.

Это вывод из кода и предыдущих кадров, а не знание о внутреннем ходе рассуждений автора. Удобство прежних функций не доказывает оригинальность композиции. Раньше качество оценивалось преимущественно по корректности расчёта, доступности controls и responsive overflow; эти проверки нужны, но сами по себе не обнаруживают шаблонную арт-дирекцию.

Обнаружено конкретное наследуемое предписание: WORKSPACE_DESIGN задаёт rail204–220px, system-sans, corners6–8px, компактную структуру workbench и отказ от serif/editorial. Это **предыдущая визуальная спецификация**, не неизменный пользовательский контракт. Новый запрос её заменяет. Остаются обязательными семантические ограничения: immutable baseline, явное происхождение результата, охват исключений, проверенные значения, режим исполнения, отсутствие ложной аттестации. AGENTS сохраняет стек и работоспособность, но не требует sidebar, cards, синего цвета или прежней страницы.

Конкретный вклад выбранных возможностей: project-bootstrap проверяет реальные границы проекта и сохранение guidance; hub-engineering обеспечивает реализацию в существующем vanillaJS/FastAPI; hub-audit отделяет независимую оценку готового интерфейса от авторской оценки. React-навыки, 3D, image generation и hosted-site generators не решают текущую задачу сами по себе. Ни установка глобальной дизайн-инфраструктуры, ни новый внешний runtime не нужны.

## Семь актуальных первичных референсов

Просмотрены оригинальные продуктовые страницы и описания студий. Доступные страницы/продуктовые демонстрации не равны тесту полного приватного приложения. Указанные ниже выводы — принципы для адаптации, не измеренная usability или основание копировать композиции. Чужие изображения, композиции и UI assets не переносились. Для реализации отдельно получены два открытых шрифта с официальных источников и сохранёнными OFL-лицензиями; см. THIRD_PARTY_LICENSES.md.

| Референс | Что непосредственно найдено | Принцип для Prooflane | Что не переносить |
|---|---|---|---|
| [Mercury Books](https://mercury.com/books) | Accounting functions показаны через конкретные задачи: reconciliation, current reports, advisor collaboration; отдельный путь Try Books Demo | Вести пользователя через предметную работу с исходниками; название действия важнее абстрактного названия модуля | Banking hero, общие банковские обещания, автоматическую категоризацию и рекламные заявления |
| [Ramp Accounts Payable](https://ramp.com/accounts-payable) | Последовательность invoice processing → approval orchestration → payment; конкретные product media и обучающие шаги | Источник, решение и передача должны быть одним связанным процессом; спорная запись остаётся в контексте | OCR/AI claims, заявленную точность, speed multipliers, payment affordances: этих возможностей в Prooflane нет |
| [Linear: Manage design projects](https://linear.app/method/manage-design-projects) | Описаны verification of problem, свободное exploration, внешняя реакция, выбор направления и handover с инженером | Сначала разные решения одной задачи, затем критика и проверка; отделять структуру от полировки | Dark sidebar, общий интерфейс issue tracker, shortcuts без visible alternatives |
| [Stripe Financial Connections](https://stripe.com/financial-connections) | Показаны отдельные selection/confirmation/success состояния; прямо объясняется состав и получатель передаваемых данных | До загрузки packet объяснить, что уходит серверу; успех привязывать к конкретному действию и его scope | Stripe gradients, банковскую модалку, безопасность/конверсию или бренды банков как свои свойства |
| [Instrument / ServiceNow](https://www.instrument.com/work/servicenow-rebrand) | Описана связная система из стратегии, type, illustration, data visualization и motion; характер выражается во многих поверхностях | Единая метафора должна определять navigation, таблицы, схему evidence и переходы, а не одну палитру | Их green identity, Youmoji, custom font или причинные claims о revenue |
| [Pentagram / SMCC](https://www.pentagram.com/work/smcc) | Приведено различие headline и text type; более выразительные формы ослаблены в text для читаемости | Выразительная display-типографика может сосуществовать с нейтральными controls и ясными monetary digits | Bespoke SMCC typeface, банковскую идентичность, буквальные формы wordmark |
| [Observable Plot: Marks](https://observablehq.github.io/plot/features/marks) | Язык charts строится из marks и position/color channels; layered marks позволяют выразить разные элементы данных | Рисовать только необходимые отношения и точные значения; selection и uncertainty использовать как разные визуальные сущности | Новую chart dependency ради вида; decorative plots, random curves, выдуманные точки |

Важная поправка исследования: открытый сегодня `runway.com` относится к Runway Creative/Dev/Robotics. Он не принят как актуальный первичный референс финансового planning-продукта. Старое знакомое имя не перенесено в research автоматически. Другие сайты/галереи могут служить ориентирами, но семь источников выше достаточны для ограниченного выбора.

## Сравнимые эскизы

Созданы три векторных листа одинакового размера1500×820. На каждом слева первый вход, справа загруженное дело. Они доступны в [локальной галерее](../../artifacts/design-studio/concepts/index.html). Это статические visual specifications: никакие нарисованные buttons не выданы за работающий прототип. Числа подписаны как synthetic concept data и соответствуют существующему demo; ни один mocked output не принят за выполненный run.

- [A — Evidence Atlas](../../artifacts/design-studio/concepts/A-evidence-atlas.svg)
- [B — Audit Folio](../../artifacts/design-studio/concepts/B-audit-folio.svg)
- [C — Comparison Theatre](../../artifacts/design-studio/concepts/C-comparison-theatre.svg)

### A. Evidence Atlas — пространственная карта происхождения

**Архитектура:** один свободный canvas, вокруг выбранного расчёта видны связанные invoice, contract, baseline, alternatives, packet. Вход — два source ports; после matching они превращаются в реальные связи. Постоянной sidebar нет. Навигация — focus node, trace parents, return-to-case; отдельный case index вызывается явно.

**Иерархия:** сначала связь и выбранный объект, затем относящиеся к нему суммы. Scientific sans, небольшие monospace IDs; тёмный лесной фон и ограниченный салатовый signal. Данные представлены графом происхождения, не рядком KPI. Выбор invoice подсвечивает путь к contract и receipt; остальные связи приглушаются, оставаясь доступными в списке. Анимация короткая и направленная вдоль выбранной связи, только при переходе focus. Reduced motion даёт мгновенное выделение.

**Риск:** до500строк превращают граф в сложный инструмент ориентации. Нужны aggregation, список эквивалентных связей, keyboard spatial policy и мобильный fallback. Оригинальность высока, но стоимость и риск ошибок интерфейса существенны.

### B. Audit Folio — аннотированное дело

**Архитектура:** полотно документа, а не shell dashboard. Вверху компактный masthead и Archive drawer; ниже четыре номерных главы. Вход — два разворота исходных регистров. Загруженный Ledger использует ruled rows; выбранная запись открывает **margin note** на том же листе. Result — типографическая строка отчёта, а не сетка карточек. Archive/history доступны из одного control и не занимают постоянную колонку.

**Иерархия:** case → scope → selected record → its source/assumptions/proof. Display Newsreader с сильной цифрой, IBM Plex Mono для source IDs и числовых пояснений, строгий system sans в controls; crisp white / тёплый нейтральный лист / чёрные правила и один oxblood accent для selection и требующего решения. Это не возвращение к старой кремовой hero: форма работы является первой композицией, заголовок не рекламирует продукт, страницы не заполняются одинаковыми карточками.

**Данные и interaction:** таблица как регистр с постоянной строковой идентичностью; references to invoice/contract rows выглядят как ссылки в примечании. При выборе записи red margin rule и inspector меняются синхронно. В Assumptions — типографические tracks с точными концами и draft/executed distinction; alternatives — comparative ledger на общей исходной базе. В Proof — связанная цепь источников и компактный execution transcript. Chapter transition меняет читаемую позицию и focus, без staggered reveals. Selection движет annotation, не весь экран. Touch получает видимую кнопку Inspect и последовательный document flow.

**Риск:** декоративная «бумага» и огромный serif могут снова съесть рабочее место. Защитные ограничения: никаких textures, drop shadows, наклонённых листов, leather/notebook clichés; плотные body14–16px; заголовок дела36–44px; цифры не вытесняют работу ниже fold.

### C. Comparison Theatre — партитура допущений

**Архитектура:** рабочая сцена сравнения; baseline закреплён сверху, alternatives — широкие синхронизированные tracks. Sources открываются в drawer перед первым запуском; Proof — отдельная outcome sheet. Нет отдельной вкладки Overview: состояние дела выражено baseline track и scope line. Навигация концентрируется вокруг выбора пары сравнения.

**Иерархия:** difference first, затем конкретные изменения и источники. Тёмный технический фон, крупные фиксированные табличные digits, сжатый sans, кислотный accent только у selected track. Данные — повторяемые строки на единой шкале, named pairs и inline changed-assumption detail. Track selection перестраивает сравнение двух состояний, остальные остаются контекстом. Shared-layout transition допустим для перемещения выбранного сравнения; сумма не анимируется через недостоверные промежуточные числа.

**Риск:** source ambiguity и исключённые счета могут казаться подготовкой, а не частью доказательства. Для Prooflane это опаснее, чем для forecasting-инструмента. Узкий мобильный экран также осложняет сравнение, требует disclosure без ложной общей шкалы.

## Предварительная авторская оценка

Это **оценка Creative Director, создавшего концепции**, не независимый audit. Независимый UX/Design Critic должен проверить эскизы до окончательного выбора. Числа — экспертные суждения, не измеренная usability. Все концепции требуют реализации и browser evidence.

| Критерий1–10 | A Atlas | B Folio | C Theatre |
|---|---:|---:|---:|
| Originality | 9: отношения формируют canvas | 8: дело определяет композицию и заметки | 8: сравнение формирует сцену |
| Visual quality potential | 8: нужна строгая дисциплина графа | 9: сильная типографика, ритм правил | 8: выразительная цифровая партитура |
| Product fit | 8: provenance центральный | 9: invoices/contracts/review подходят метафоре | 7: альтернативы затмевают основания |
| Usability potential | 6: spatial orientation незнакома | 8: главы, регистр и примечание читаемы | 7: легко сравнивать, сложнее начать |
| Interaction quality potential | 9: связь выбора и происхождения | 8: source-to-note-to-proof continuity | 8: синхронные comparisons |
| Technical feasibility | 5: graph, keyboard и500rows дорогие | 9: семантические HTML, CSS и existing API | 7: новая сравнивающая навигация |

**Рекомендация: B, Audit Folio.** Она изменяет архитектуру страницы, а не только цвет. При этом existing DOM/API behaviour можно сохранить: исключения и scope остаются на первом плане, источники доступны рядом с записью, execution provenance не превращается в декоративный trust badge. Вклад A стоит оставить как точный trace выбранной записи внутри Proof, а не переносить весь canvas. Вклад C полезен в сравнении вариантов на общей baseline, но не должен скрывать source decisions. Это выбор принципов, а не смешение трёх поверхностей в новый dashboard.

## Конкретная спецификация для выбранного направления

- **Visual metaphor:** открытое review file с регистром и полем аннотаций. Одна большая поверхность с разделительными правилами, а не общий dashboard фон с островками.
- **Tokens:** paper `#F4F3EF`, sheet `#FFFDF9`, ink `#25221D`, secondary `#68635D`, rule `#CEC8BE`, annotation `#7F2631`. Это предложенные tokens финальной реализации; draft B использует более красную аннотацию как первоначальный вариант. Цвет решения не заменяет слова Unresolved/Selected/Excluded. Не использовать одновременно четыре semantic badge palettes.
- **Typography:** case headings — локальный Newsreader; body/controls — Segoe UI/Arial; source IDs and monetary detail — локальный IBM Plex Mono. Display36–44px; body14–16px; essential labels≥12px. Serif не применять к длинным таблицам, inputs, error или runtime transcript. Шрифты обслуживаются с того же origin; никаких глобальных установок или внешних font requests при работе приложения. Root проверил официальные Google Fonts repositories и владеет получением локальных font files и OFL-лицензий. Первичные источники: [Newsreader](https://github.com/google/fonts/tree/main/ofl/newsreader), [IBM Plex Mono](https://github.com/google/fonts/tree/main/ofl/ibmplexmono). Статический SVG-эскиз использует доступные Georgia/Consolas fallback: он показывает геометрию и иерархию, а не подтверждает вид ещё не подключённых webfonts. В финальном продукте выразительность Newsreader должна проверяться по реальному browser render.
- **Geometry:** header ориентировочно76px; chapter line48px; main gap24–32px; ruled section spacing28px; controls40px desktop/44px touch. Border radius0–3px только у controls, отсутствие shadows и декоративных gradients.
- **Composition:** header brand left, case utilities right; Archive — drawer/dialog; case title+scope в общем masthead. Sources как facing columns, Ledger как широкий register+margin note, Assumptions как плоскость точных comparative tracks, Proof как document chain+transcript. На новом деле ни пустых финансовых metrics, ни декоративной hero illustration.
- **Responsive:** ≥1200px ledger и margin note примерно2.1:1; tablet768–1199px detail раскрывается под выбранной строкой/в full-width region без узкой колонки; mobile320–767px document flow и ясные buttons, header utilities в disclosure, chapter links остаются достижимыми, intentional table scroll подписан. Источник и сумма выбранного invoice не теряются при переходе к proof.
- **Interaction thesis:** «Выбрать утверждение — увидеть его основание — испытать допущение — сохранить проверяемый след». Selection accent и annotation делают этот переход наблюдаемым. Не добавлять drag там, где пользователь должен точно выбрать юридически значимый источник.
- **Motion:** 120–180ms translation annotation на6–10px при selection; контекстный linked-focus outline; progress показывает настоящий запрос/этап, а не симулированный процент. `prefers-reduced-motion` отключает translation/transition, оставляя state/focus.
- **Access:** живые числовые значения никогда не доступны только hover; кнопки Inspect имеют row-specific name; выбранное состояние выражено `aria-pressed/current` и текстом; keyboard/focus продолжают путь источника; Archive закрывается Escape и возвращает focus; alerts не стирают draft. Не кодировать статус только vermilion цветом.

## Признаки, по которым нужно отвергнуть реализацию

Если после удаления синего цвета остаются та же левая rail, KPI cards, одинаковые rounded panels и длинная сетка модулей, концепция не реализована. Если большая красивая «обложка» опускает match/create ниже полезного первого экрана, это повтор старой ошибки. Если анимация позволяет принять estimate/draft за выполненный альтернативный run, её надо удалить. Если proof показывает абстрактную схему без выбранной invoice/contract identity, метафора стала декорацией.

Готовый интерфейс оценивается только после desktop/tablet/mobile interaction и screenshots. Этот документ не закрывает такие проверки.


## Дополнительное визуальное наблюдение root

В отдельной Chrome-вкладке фактически открыты Mercury Books и Instrument/ServiceNow; прочитано состояние и просмотрены отрисованные страницы. У Mercury метафора книги выражена крупным иллюстративным объектом и отдельной иерархией продукта; у Instrument выразительная типографика доминирует над контейнерами. Для рабочего Prooflane эти маркетинговые hero и их размер не перенесены: источники и действие сверки должны оставаться доступными сразу. Это визуальное наблюдение двух публичных страниц, не испытание их закрытых приложений или измерение usability. Внешние изображения и видео не загружались в проект.
