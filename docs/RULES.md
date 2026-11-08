# Правила и источники конкурса

Повторно проверено 2026-11-06, часовой пояс пользователя Asia/Qyzylorda. Это исследовательский снимок публичных правил, а не подтверждение допуска или подачи. Личная регистрация и закрытая форма подачи не проверялись.

## Источники

| Код | Официальный источник | Прочитанные разделы |
|---|---|---|
| E | [Vultr: Agent Rush](https://lablab.ai/ai-hackathons/vultr-hackathon) | Challenge playbooks; Technology & Access; Guidelines; What to submit; Judging criteria; Event Schedule |
| R | [Rule Book](https://lablab.ai/hackathon-rules) | Submission Guidelines; Judging Criteria; Deadline; Ethical Conduct |
| S | [Submission Guidelines](https://lablab.ai/delivering-your-hackathon-solution) | §§1–3, 5–6 |
| G | [Getting Started](https://lablab.ai/getting-started-guide) | Introduction; Registration; Event Timeline |
| T | [Terms of Use](https://lablab.ai/terms-of-use) | §§3, 4, 16; страница указывает редакцию 2025-07-01 |
| H | [Tutorial](https://lablab.ai/ai-articles/hackathon-guidelines) | Submission; опубликован 2026-02-25 |

## Реестр условий события E

| ID | Условие | Раздел |
|---|---|---|
| E01 | Онлайн: 3–8 ноября 2026; очно: 8 ноября, Salt Lake City | Overview |
| E02 | 8 ноября 23:00 UTC, 9 ноября 04:00 Asia/Qyzylorda. Подтверждено в браузере | Event Schedule |
| E03 | Команда: 1–6 участников | Teams |
| E04 | Backend VM и веб-приложение на Vultr; Vultr управляет процессом | Technology |
| E05 | C1: LLM-вызовы через Vultr Serverless Inference | Technology |
| E06 | C1: изолированное выполнение; Docker рекомендован | Technology |
| E07 | C1: отделение от host/app runtime | Containment |
| E08 | C1: без ключей/учётных данных в sandbox | Containment |
| E09 | C1: ограничения времени/памяти | Containment |
| E10 | C1: reset/destroy после задачи | Containment |
| E11 | C1: код → выполнение → результат → объяснение; browser-паттерн альтернативный | Playbook |
| E12 | C1: показать containment moment в видео | Submission |
| E13 | README: Vultr, архитектура, сценарий, реальные действия | Vultr documentation |
| E14 | Подача на lablab.ai обязательна; Vultr Community опционально | Submission |
| E15 | Четыре критерия: Application of Technology, Presentation, Business Value, Originality; веса не опубликованы | Judging |
| E16 | Заявлены $200 кредитов; активация аккаунта пользователя не проверена | Credits |
| E17 | Vultr GPU недоступны; C2 допускает необязательный Inference | Technology |
| E18 | Cover перечислен среди материалов события | What to submit |

## Общие условия и форматы

- **T01:** условия сервиса указывают возраст 18+, полномочия принять условия и отсутствие предшествующего запрета аккаунта. Персональное соответствие **UNKNOWN**. [T, §3](https://lablab.ai/terms-of-use).
- **T02:** работа должна быть оригинальной, открытой и совместимой с MIT, если событие не задаёт исключение; нужны права на используемые материалы. [T, §§4, 16](https://lablab.ai/terms-of-use).
- **G01:** регистрация события, заполненный профиль, связанный Discord и членство на сервере; solo-команда допустима. Подавать может администратор команды или до трёх назначенных участников. [G](https://lablab.ai/getting-started-guide).
- **R01:** публичный GitHub, доступный URL приложения, видео MP4/MOV и PDF-слайды требуются по умолчанию. [R, Submission](https://lablab.ai/hackathon-rules).
- **R02:** плагиат, накрутка и несанкционированная автоматизация могут привести к дисквалификации. Обещать, что любая автоматизация разрешена, нельзя. Локальная разработка отделена от автоматической подачи. [R, Ethical Conduct](https://lablab.ai/hackathon-rules).
- **R03:** общий Rule Book упоминает пяти­минутный grace period; внутренний план не должен на него рассчитывать. [R, Deadline](https://lablab.ai/hackathon-rules).
- **S01:** стандартная форма: название 5–50 знаков, краткое описание 50–255, полное 600–2000; категории, технологии, платформа/URL и режим участия online/onsite. [S, §§1, 3](https://lablab.ai/delivering-your-hackathon-solution).
- **S02:** видео до 300 MB; менее пяти минут — рекомендация. Cover по общему guide необязателен, формат 16:9. [S, §2](https://lablab.ai/delivering-your-hackathon-solution).

## Приоритет и неопределённости

Event page и фактическая submission form имеют приоритет над общими инструкциями — это прямо сказано в [R](https://lablab.ai/hackathon-rules), [S](https://lablab.ai/delivering-your-hackathon-solution) и [G](https://lablab.ai/getting-started-guide). При конфликте самой формы со страницей нельзя самостоятельно объявлять одну отменённой: сохранить расхождение и получить ответ организаторов до подачи.

1. [H](https://lablab.ai/ai-articles/hackathon-guidelines) задаёт минимум 100 слов для длинного описания; S задаёт диапазон знаков. Рабочее решение: подготовить текст, удовлетворяющий обоим, затем сверить форму.
2. E18 перечисляет cover, тогда как S считает его опциональным. Подготовить cover; не полагаться на необязательность.
3. R описывает общую шкалу 1–5. Для этого события подтверждены только названия критериев E15. Не выдавать внутренние веса и баллы за официальные.
4. Ограничения по стране, необходимость физического присутствия для финального judging, отдельные правила допустимости AI-assisted разработки и ранее написанного кода — **UNKNOWN** по изученным разделам. Отсутствие найденного запрета не равно разрешению. Организаторам сообщений не отправляли.
5. Кредиты из E16 не подтверждают баланс пользователя и не разрешают расходы. Бюджет проекта остаётся $0 до подтверждённого доступа и разрешённого использования ресурсов.

## Решение проекта

Рабочая рекомендация: **Challenge 1 / Blast Radius Zero, code-execution pattern**. Предполагаемый продукт — CSV-аналитик с воспроизводимыми вычислениями и проверяемыми результатами. Это наш выбор реализации, а не новое требование организатора. Подтверждение прохождения каждого gate ведётся в [REQUIREMENTS.md](REQUIREMENTS.md); прочитанное правило не считается выполненным требованием.
