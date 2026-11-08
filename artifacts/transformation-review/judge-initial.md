**Независимый начальный review трансформации Prooflane.** 2026-11-03; первоначальная выборка около 18:52 UTC. Роль: строгий конкурсный рецензент и исследователь первичных источников. Проверены исходные доказательства; прежние judge-initial/cycle1/cycle2 не использованы для вывода. Файлы продукта не редактировались.

**Вердикт:** локальная арифметика и переносимая проверка уже имеют доказательства. Продуктовая самостоятельность и оригинальность текущего пути недостаточны: источник договорной цены находится в самом invoice CSV; what-if ограничен одной ячейкой; полезность генерации кода для заранее заданной формулы не показана. Добавление ещё одного summary или красивого графа это не исправит. Облачная часть не подтверждена и не может быть засчитана по локальным артефактам.

| Проверенный материал | Наблюдение | Граница |
|---|---|---|
| `prooflane/analysis.py` | Колонки invoice_id/vendor/quantity/unit_price/contract_price/notes; fixed Decimal positive variance | Нет contract source/date/item join |
| `prooflane/comparison.py` | Два receipts, одна числовая ячейка, immutable baseline, проверка lineage/delta | Нет board нескольких альтернатив или dated applicability |
| `prooflane/receipts.py` | Хеши и независимый пересчёт fixed arithmetic | Не аутентифицирует договор, издателя или runtime |
| `prooflane/provider.py` | VSI-only adapter, fixed-rule program generation, raw CSV не входит в generate payload | Адаптер не доказывает live call и полезность AI |
| `web/index.html` | Один путь review→inspect→compare→keep, честные reference/integrity labels | Статическое чтение HTML, не browser usability test |
| `artifacts/optimization/final/scenario-smoke.json` | Сохранены 36 успешных checks, reference/Docker и 0 model calls | Это read existing evidence, не повторный HTTP smoke |

Собственное воспроизведение: из `D:\projects\vultre` выполнены `.\.venv\Scripts\python.exe scripts\verify_receipt.py artifacts\optimization\final\reference-comparison.json` и `.\.venv\Scripts\python.exe scripts\verify_receipt.py artifacts\optimization\final\sandbox-comparison.json`. Обе команды: exit 0, `passed: true`; baseline 1480.00, scenario 1160.00, delta −320.00, неизменных записей 23. Проверены данные двух существующих артефактов; Docker/Vultr/model не вызывались. Console output не сохранялся как отдельный log, результат зафиксирован здесь. Hashes ниже связывают review с прочитанными файлами и не удостоверяют время/авторство.

| Файл на момент review | SHA-256 |
|---|---|
| `prooflane/analysis.py` | `08008D679DDAE3FA1E231C3F26EA1A6211D8B9FA1639EA05CA201A16B3A24817` |
| `prooflane/comparison.py` | `FAE43016D4E09A47F7AF92D6FFD615319256E5B62FCE73FED89077C2BC08366A` |
| `prooflane/receipts.py` | `F873DECC606C79F2B6AD392BA48BC50555C533E440CD824776461EA60949B275` |
| `artifacts/optimization/final/sandbox-comparison.json` | `6E3381555334A0F73AABA7FBA3A4AA14449F778F443E7BEA6806C9AF5C516C4C` |

**Сильнейшие вопросы к защите проекта:**

1. Кто установил, что `contract_price` относится именно к этой позиции и периоду? Точный Decimal не исправляет ошибочный join.
2. Почему пользователь не выполнит эту задачу в Excel, где уже есть сценарии и таблицы подстановок? Нужна сравнительная задача, не утверждение о новизне.
3. Что модель добавляет к уже известной формуле? Пока live benefit и real VSI behaviour неизвестны.
4. Что означает отсутствие finding: цена корректна, нет договора или данные не поддерживаются? Эти состояния нельзя объединять в ноль.
5. Что проверит получатель без доверия серверу? Пересчёт данных полезен; self-reported execution и исходный документ остаются вне доказательства.
6. Почему invoice–contract matching необычен, если AppZen прямо описывает такой workflow? Обосновать узкую комбинацию и доступную проверку, не общий AP use case.
7. Кто проверил, что пользователю нужен offline packet? Интервью и handoff experiment отсутствуют.

Официальные требования и четыре критерия проверены на [странице события](https://lablab.ai/ai-hackathons/vultr-hackathon) и в [Rule Book](https://lablab.ai/hackathon-rules), 2026-11-03. Точный deadline/timezone остаётся неизвестен. Численные initial оценки и правила пересмотра находятся в [COMPETITIVE_SCOREBOARD.md](../../COMPETITIVE_SCOREBOARD.md). Они не предсказывают результат конкурса.

**Рекомендация:** 1) раздельные invoices/contracts с exact dated join; 2) coverage и unresolved exceptions; 3) immutable named alternatives; 4) bounded sensitivity/break-even; 5) offline case packet с семантической проверкой связей. Обоснование, 26 возможностей, licensing/unknowns и отвергнутые направления: [TRANSFORMATION_RESEARCH.md](../../docs/TRANSFORMATION_RESEARCH.md).

Уверенность: высокая в существующем арифметическом baseline и обнаруженном semantic gap; средняя в реализуемости ограниченного нового пути; низкая в превосходстве над альтернативами, пользе AI и готовности конкурса. Пересмотр возможен после фиксированного ручного oracle, нового full workflow и rehashed semantic tamper controls. До этого post-оценка — NOT_REVIEWED.
