# Prooflane — final submission copy

**Track:** Blast Radius Zero  ·  **Participation:** Online

**Title**

Prooflane

**Short description (187 characters)**

Trace invoice price disputes to dated contracts. Run AI-generated analysis in isolated Vultr containers, challenge shared assumptions, and hand reviewers an independently verifiable case.

**Long description (1755 characters)**

Accounts payable teams can spot a price difference in a spreadsheet, yet still struggle to explain which contract applied and reproduce a colleague's decision. Prooflane turns that dispute into a reviewable case.

Upload invoice and contract CSVs. Exact supplier, item and date matching identifies eligible prices. A reviewer resolves overlapping contracts or records an exclusion reason before the baseline is frozen. Shared-contract what-if changes propagate to every linked invoice. Exact uncertainty ranges and cent-level priority boundaries show which source to confirm next. These are declared assumptions, not predictions.

A Vultr Cloud Compute VM hosts the web app, SQLite and orchestration. Vultr Serverless Inference generates Python; disposable Docker executes it without network access, host mounts or injected credentials, with time and resource caps. An independent Decimal verifier checks every reported variance. After verification, Vultr selects the focus of guidance; the server supplies the checked amounts. Failed or mismatching output is withheld.

Our real public-browser AI run processed seven of eight fictional invoices and independently verified USD 768 in positive price variance. The interface exposes both Vultr request IDs and execution provenance. Fresh browser containment probes confirmed denied network access and root writes, absent inference credentials, non-root execution and container cleanup.

Download CSV, a review brief or a hash-linked JSON case packet. The packet verifier reconstructs sources, arithmetic and priority boundaries offline. This proves consistency, not supplier identity, contract truth or recovered savings. Our next test measures how reliably a second reviewer can reproduce the same dispute.

**Team members**

Nurali Kuzhagaliev, Nuraiym Kilybayeva, Mariyam Murzagaliyeva, Abylay Tabayev

**Demo:** https://45.76.92.198/

**GitHub:** https://github.com/NuraliKuzhagaliev/Prooflane

[MP4](../submission/agent-rush/video/prooflane-demo.mp4) · [PDF](../submission/agent-rush/prooflane-deck.pdf) · [Cover](../submission/agent-rush/cover.png)

Кандидатные категории: AI Agents, Finance & Accounting, Data Analysis, Cybersecurity. Технологии: Vultr, Vultr Serverless Inference, Python, Docker, FastAPI, JavaScript, SQLite. Выбрать существующие варианты в форме.

Состав подтверждён пользователем; роли и официальное название команды не предоставлены. Заявка не отправлена. [Файлы и порядок загрузки](../submission/agent-rush/README.md) · [Проверка требований](FINAL_SUBMISSION_20261109.md).
