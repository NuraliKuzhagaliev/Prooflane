# Пакет презентации Prooflane

Обновлено 2026-11-03. Состояние: **локальный прототип; Vultr и финальная конкурсная подача ещё не проверены**.

## Готовые файлы

- `prooflane-deck.pptx`: 6 слайдов; редактируемые тексты, две native-таблицы и схема архитектуры.
- `prooflane-deck.pdf`: 6 страниц 16:9, растровая визуальная копия слайдов. Для редактирования и копирования текста используйте PPTX.
- `cover.png`: 1600 × 900, обложка с настоящим скриншотом локального приложения.

Новая история: исходная проверка → одно числовое допущение → отдельный запуск тем же способом → точная разница → пакет с обеими квитанциями. Исходный результат сохраняется. Слайды явно называют сценарий гипотетическим; уменьшение variance не названо экономией или возвратом денег.

## Источники фактов

- Слайд 1: `artifacts/optimization-review/frontend/reference-comparison.png`, настоящий browser screenshot reference-режима с синтетическими данными. Это не live AI.
- Слайд 2: `artifacts/optimization-review/frontend/mobile-source.png`, настоящий диалог исходной строки с действием Test an assumption.
- Слайд 3: `artifacts/optimization/sandbox-comparison.json`, исходный run `dbc6b4fd-b34f-4569-815f-955165f87297` и scenario `5eccc9f5-fb6d-4957-8318-a16fe71042bf`. Контрактная цена строки 3: 72 → 80; общая variance 1480 → 1160; delta −320; строка 520 → 200; 23 другие записи не изменены; billed остаётся 34353. Оба запуска — настоящий локальный Docker с фиксированным рецептом.
- Слайд 5 после второго judge review: строка названа `Scenario + original`, явно указано `Checked together in packet`. Проверка ровно одного изменения, связи с исходной квитанцией и наследования режима требует обеих квитанций в `check_bundle`; отдельный `check_receipt` эту связь не подтверждает. Это также уточнено в speaker notes.
- Слайд 6: 83 Python tests из `artifacts/optimization/windows-cycle1.txt`, 24 HTTP cases из `artifacts/optimization/evaluation.json`, 36 scenario smoke assertions из `artifacts/optimization/scenario-smoke.json`. Это разные, частично пересекающиеся проверки, не оценка точности модели.
- Источники и границы утверждений указаны в speaker notes каждого слайда. Live Vultr Inference, облачный VM, публичный доступ и подтверждение пользы пользователями остаются pending.

## Воспроизведение

Использованы существующий bundled `@oai/artifact-tool`, ReportLab fallback и Poppler. Новые зависимости не устанавливались, глобальные настройки не менялись.

```powershell
& 'C:\Users\nural\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' scripts/build_submission.mjs
```

Сборщик сам вызывает `scripts/verify_receipt.py` для comparison packet и прекращает экспорт при ошибке. Денежные поля форматируются из decimal strings без преобразования в Number. Показатели проверок считываются из сохранённых evidence-файлов. Сборщик: `scripts/build_submission.mjs`; PDF fallback: `scripts/build_submission_pdf.py`. При переносе получите актуальные пути через `load_workspace_dependencies`.

## Реальная проверка этой версии

- Artifact Tool export/import, package integrity, layout, fonts: PASS; 6 слайдов, 0 findings, 0 warnings.
- Native-таблицы слайдов 3 и 5 сохранены. Проверка native-table arithmetic пропущена для их неаддитивной структуры; фактические дельты проверены независимым CLI до построения таблицы.
- Все шесть слайдов просмотрены индивидуально после рендера; перенос текста на обложке исправлен и заново отрисован.
- PDF повторно отрисован Poppler; все шесть страниц просмотрены, обрезания и наложения текста не обнаружены.
- После уточнения слайда 5 пересобраны PPTX и PDF; изменённый слайд просмотрен в Artifact Tool PNG и новом Poppler-рендере страницы 5, без обрезания или наложений. Validation receipt: `submission/.build/validation-2026-11-03T18-39-42-067Z.json`, 0 findings и 0 warnings.
- PDF structure: 6 страниц по 1200 × 675 pt, без JavaScript и шифрования.
- PowerPoint UI: NOT_RUN. Проверка экспорта и импорта не является проверкой приложения Microsoft PowerPoint.
- SHA-256 итогового PPTX: `f9f3721e00c38f948b5cb34822e3e92b5590cfdb0a90eeb8b0d3a5767f4a4218`.
- SHA-256 итогового PDF: `69b646867163583c8f4123cd944998b2a1243e0761e53bf8e7dcab2ec82a254e`.

Существующие ограничения runtime сохранены: при отказе hard link используется локальный exclusive-copy fallback только в `submission/.validated`; package/layout/import/hash проверки остаются. Прямой PDF export не разрешает alias `#standard-fonts/Helvetica`, поэтому ReportLab собирает PDF из проверенных PNG. Это явно растровая PDF-копия. Частные build-артефакты и validation receipt находятся в `submission/.build/` и `submission/.validated/`; судьям они не нужны.
