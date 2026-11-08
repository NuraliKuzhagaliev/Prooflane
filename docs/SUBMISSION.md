# Материалы подачи Prooflane

Пакет подготовлен для LabLab, Blast Radius Zero. На 9 ноября публичный API, Docker, живой Inference через браузер и публичный GitHub проверены. Финальное видео и подтверждение отправки остаются открытыми. Исторический срок подачи и ограничения его повторной проверки приведены в [требованиях и доказательствах](AGENT_RUSH_READINESS.md).

**Title**

> Prooflane

**Short description**

> Trace disputed invoice prices to contract versions, test shared assumptions, and hand reviewers a case they can verify offline.

**Long description**

> Prooflane helps accounts payable and procurement teams investigate differences between billed and contracted prices. Upload two CSVs. The system matches invoices by vendor, item and effective date. A reviewer chooses between overlapping contracts or records why an invoice is outside scope.
>
> The original result stays fixed. Changing one shared contract price recalculates every linked invoice. Declared bounds show how far the total could move and which source is worth confirming first. A downloaded case packet lets a second reviewer reproduce the matching, arithmetic and what-if changes offline.
>
> A Vultr VM hosts the app, data and execution controls. Python runs in disposable Docker containers with resource limits and no network or host mounts. An independent Decimal checker verifies each reported variance. The Vultr agent is designed to obtain code from Serverless Inference and, after verification, ask the model to choose the emphasis of an explanation. The model receives task context and counts. Prooflane fills in verified amounts locally.
>
> A live run through the public API used DeepSeek V4.1 Flash to generate Python and select the emphasis of the explanation. Docker processed seven of eight fictional invoices. An independent verifier reproduced the $768 positive variance from the saved case packet. The public demo also offers a fixed Docker recipe.

- **Technology tags** · Vultr, Vultr Serverless Inference, Python, Docker, Data Analysis, AI Agents. Сверить доступные теги в форме.
- **Demo platform** · Vultr Cloud Compute.
- **Demo URL** · [Prooflane](https://45.76.92.198/).
- **GitHub** · [NuraliKuzhagaliev/Prooflane](https://github.com/NuraliKuzhagaliev/Prooflane).
- **Slide PDF** · [Готовый PDF](../submission/agent-rush/prooflane-deck.pdf).
- **Editable slides** · [PPTX](../submission/agent-rush/prooflane-deck.pptx).
- **Cover** · [PNG 16:9](../submission/agent-rush/cover.png).
- **Video** · [Сценарий](DEMO.md). Браузерный AI-прогон выполнен; финальная запись не подтверждена.
- **Participation mode** · Указать фактический режим участия в форме.

Сверить поля с активной формой LabLab. [Стандартные лимиты полей](https://lablab.ai/delivering-your-hackathon-solution) · [Доказательство живого запуска](../artifacts/vultr-release/live-evidence.json).
