# Готовое демо, 9 ноября

[MP4](../submission/agent-rush/video/prooflane-demo.mp4) · [English transcript](../submission/agent-rush/video/transcript.en.txt) · [English SRT](../submission/agent-rush/video/prooflane-demo.en.srt) · [Фактические таймкоды](../submission/agent-rush/video/video-manifest.json).

Ролик длится около 3:58 и содержит английскую локальную синтетическую озвучку и встроенные субтитры. Это монтаж настоящих браузерных кадров, не непрерывная запись экрана. Сохранённый AI-прогон 9 ноября назван сохранённым, новые пять containment-проб и повторная проверка пакета выполнены при финальной подготовке. Секреты не вводились и в ролик не попали. [Описание производства](../submission/agent-rush/video/PRODUCTION.md).

Ниже сохранены прежние сценарии для отдельной записи живого выступления. Они не описывают уже записанное непрерывное видео.

# Historical product walkthrough — 2:45, 8 November

This is a script, not a claim that a final video was recorded. Use fictional inputs, keep the mode visible, and do not show operator credentials. The new one-click example is Reference; it must never be presented as live AI. A live VSI recording needs its own successful request; the saved November6 evidence may be shown only as a labelled previous run.

| Time | Action | Observable point |
|---|---|---|
|0:00–0:20|Open https://45.76.92.198/ → Open a reviewed example|AP reviewer sees768 positive price variance and7of8 included rows. The preset choice/exclusion is disclosed.|
|0:20–0:50|Sources → INV504, then INV506|Eligible contracts give40/32 conditional invoice variance;250 billed is outside scope, not zero variance or savings.|
|0:50–1:15|Ledger → C1|One source price binds3 rows, including INV508 with zero original variance. Filter/reset the exact group.|
|1:15–1:45|Assumptions → price priority boundary → Try82.60|82.59 keeps INV501 first;82.60 is a tie;82.61 changes the leader. Other inputs stay original. An alternative is prepared, not silently executed.|
|1:45–2:15|Proof → contract/source nodes → download CSV, brief, packet|Show row lineage and three handoff formats. Only JSON is independently reconstructed by the verifier.|
|2:15–2:45|Run containment check; show original packet pass and duplicate-key/tampered packet rejection|Actual Vultr Docker probe outcomes. State limits: hashes do not authenticate a contract or issuer.|

Fallback: the reviewed Reference example remains usable without a key or Docker, with its mode shown. For actual isolated execution choose the manual fictional review and Sandbox recipe; allow its execution time rather than cutting it into a purported live AI clip. Detailed script for the original provider-focused walkthrough follows as historical guidance.

---

# Сценарий демо Agent Rush

Целевой хронометраж 3:50. Основной вариант для Blast Radius Zero записывается после настоящего запуска Inference. Вводить operator token до записи либо поставить запись на паузу и скрыть поле. Ключ подписки хранится только на VM. Использовать встроенный вымышленный пример.

| Время | Что показать | Что сказать |
|---|---|---|
| 0:00–0:35 | Слайды 1–2, затем Sources → Try the fictional review | “An invoice is disputed. Before we calculate, we need to establish which contract price applies.” |
| 0:35–1:10 | INV504 → C2R, INV506 → exclusion with reason, семь строк в расчёте | “One overlapping agreement needs a choice. A second invoice has no active supplied contract. Both decisions stay in the case.” |
| 1:10–1:55 | Baseline execution → Vultr agent → Create baseline. Ledger, затем Proof → Baseline execution, code and receipt | “The model produced Python, the VM ran it in disposable Docker, and an independent checker verified every reported variance.” Назвать фактическую модель, ID запроса и сумму. Упомянуть объяснение модели только при её фактическом успешном ответе. |
| 1:55–2:30 | Assumptions → задать C1 $65–85 и INV501 quantity 20–80 | “The declared ranges put total positive variance between $148 and $1,993. Confirming C1 removes at least $645 of that uncertainty.” |
| 2:30–3:10 | Proof → Run containment check. Показать отказ записи в root filesystem, отсутствие переменной ключа и подтверждённое удаление контейнера | “These checks just ran on the Vultr VM in a fresh container. Here are the observed outcomes.” |
| 3:10–3:50 | Export case packet → проверка CLI → слайды 5–6 | “A second reviewer can check the sources and recalculate the result without access to our service.” Показать пройденную проверку и назвать границы доказательства. |

Во время генерального прогона сверить $768 baseline, 7 из 8 строк и 5 положительных отклонений. При сбое модели оставить его видимым. Для отдельного резервного ролика выбрать Sandbox recipe и обозначить, что это фиксированный Python с независимой проверкой. Этот вариант демонстрирует реальную работу Docker, а проверку VSI нужно записать отдельно после успешного запроса.

В [облачном отчёте](../artifacts/vultr-release/case-http-smoke.json) уже есть положительный прогон и отрицательный контроль с изменённым значением и пересчитанным хешем. Команда офлайн-проверки: `python scripts/verify_receipt.py prooflane-case.json`. После записи открыть готовый MP4/MOV, проверить время, размер и отсутствие секретов, сохранить ссылку рядом с [материалами подачи](SUBMISSION.md).
