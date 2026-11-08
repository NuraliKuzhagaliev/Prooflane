# Развёртывание Prooflane на Vultr

**Публичное приложение работает на Vultr.** [Демо по HTTPS](https://45.76.92.198/). Inference ещё выключен. На существующей VM пользователь вставляет ключ подписки через `sudo nano /opt/prooflane/.env`, только в значение `VULTR_INFERENCE_API_KEY`. Модель `deepseek-v4.1-flash-1017` уже записана в конфиг. После сохранения оператор проверяет подписку, задаёт отдельный operator token, включает live, перезапускает сервис и выполняет синтетический тест. [Как найти ключ подписки](https://docs.vultr.com/products/compute/serverless-inference/management/connection).

## Если вы впервые создаёте сервер

VM не нужно скачивать на ноутбук. Это отдельный компьютер в облаке Vultr: после создания у него появится IP-адрес, и подключение выполняется через SSH. Локальный Docker Desktop остаётся инструментом разработки; он не заменяет обязательный сервер Vultr.

1. **Сначала подготовьте SSH key.** Если уже есть подходящий ключ, используйте его. Иначе в PowerShell создайте отдельный Ed25519 key, задайте passphrase и сохраните приватную часть только у себя. Не перезаписывайте существующий ключ. В [Vultr SSH Keys](https://docs.vultr.com/products/orchestration/ssh-keys/add-ssh-keys) добавляется только содержимое файла с окончанием `.pub`; ключ выбирается при создании VM.
2. В консоли выбрать **Cloud Compute**, Linux **Ubuntu 24.04 LTS**, обычный CPU. Рабочая рекомендация для начала: 2 vCPU и 2–4 GB RAM; это инженерная оценка, не измеренный capacity benchmark. GPU для проекта не нужен. Проверить регион, текущую цену, срок кредита и покрывает ли купон выбранную услугу. Только после этого участник подтверждает создание; приложение не создаёт VM автоматически.
3. Выбрать загруженный SSH public key. При доступной опции **Limited User Login** включить её; обычно создаётся `linuxuser` с возможностью `sudo`. Это отдельный пользователь входа, не service account `prooflane`. [Официальное объяснение](https://docs.vultr.com/support/platform/ssh-keys/how-do-i-use-an-ssh-key-with-a-non-root-user-on-a-vultr-instance).
4. После готовности записать публичный IP, регион/OS, имя входа и путь к приватному ключу на вашем компьютере. Можно сообщить инженеру IP и имя пользователя; **приватный ключ, passphrase и пароли в чат не отправлять**. Подключение: `ssh -i PATH_TO_PRIVATE_KEY linuxuser@YOUR_VM_IP`. Проверить SSH host fingerprint по доверенному каналу/консоли перед первым подтверждением.
5. **Vultr Serverless Inference — отдельное подключение.** Создание VM и купон не означают, что оно уже доступно. Проверить активную subscription, её условия и разрешённый расход; получить API key и доступный model ID. Заполнять ключ локально в `.env`, не в сообщении. [Инструкция получения Inference key](https://docs.vultr.com/products/compute/serverless-inference/management/connection).

Пример самостоятельной генерации ключа при отсутствии существующего (не выполняется приложением):

```powershell
$sshDirectory = Join-Path $env:USERPROFILE '.ssh'
New-Item -ItemType Directory -Force -Path $sshDirectory | Out-Null
$keyPath = Join-Path $sshDirectory 'prooflane_vultr'
if (Test-Path -LiteralPath $keyPath) { throw 'Key already exists; use it or choose another name.' }
ssh-keygen -t ed25519 -f $keyPath -C 'prooflane-vultr'
Get-Content -LiteralPath ($keyPath + '.pub')
```

Только последняя команда показывает **публичную** часть, которую можно добавить в Vultr. Путь без `.pub` содержит приватный ключ.

## Предварительные условия сервера

- Выделенная VM Vultr без чужих сервисов/данных. Административный SSH-доступ подтверждён; никакой автоматической покупки или billing setup.
- Docker Engine для Linux, Caddy и Python с `venv`. Локально проверен Python 3.13.2; системный Python Ubuntu 24.04 может отличаться, поэтому чистый Linux install и полный тестовый набор — обязательный отдельный gate. Не подключать произвольный PPA ради совпадения номера версии.
- Docker/Caddy устанавливаются по проверенным пакетным инструкциям: [Docker Ubuntu](https://docs.docker.com/engine/install/ubuntu/), [Caddy packages](https://caddyserver.com/docs/install). Здесь нет команд `curl | sh` и автоматического изменения всей VM.
- На действующей VM Caddy использует публичный сертификат IP. При новом развёртывании можно использовать контролируемый DNS hostname с собственным сертификатом. TCP 80/443 открываются для Caddy, SSH ограничивается администраторскими адресами. 8765 и Docker daemon не выставляются наружу.

Не применяйте инструкции первой установки поверх уже существующего `/opt/prooflane` или чужого systemd/Caddy config. В таком случае сначала сохранить текущие конфигурации и подготовить отдельный release/rollback.

## Копирование исходников

После подтверждённого доступа создать staging directory на новой VM:

```sh
mkdir -p ~/prooflane-upload
```

В PowerShell из корня проекта скопировать только необходимые исходники (подставить реальный IP и при необходимости добавить `-i PATH_TO_PRIVATE_KEY`):

```powershell
scp -r prooflane web sandbox examples scripts deploy docs tests requirements.lock pytest.ini README.md RESEARCH.md INNOVATION.md TESTING.md SECURITY.md LICENSE .env.example linuxuser@YOUR_VM_IP:~/prooflane-upload/
```

`.env`, `.venv`, `.git`, локальная БД, кэши и чужие файлы в команду не включены. В Python source directory могут быть `__pycache__`; они не нужны на сервере, не являются частью воспроизводимого build и должны быть исключены из окончательного release archive.

## Первичная установка на подтверждённой выделенной VM

Следующие команды предназначены для оператора новой VM; при существующем service user/path сначала проверить владение и не повторять создание вслепую. Пример использует уже установленный `python3` и требует его проверки:

```sh
python3 --version
docker --version
caddy version
sudo useradd --system --home /opt/prooflane --shell /usr/sbin/nologin --user-group prooflane
sudo install -d -o root -g root -m 0755 /opt/prooflane
sudo cp -R ~/prooflane-upload/. /opt/prooflane/
sudo chown -R root:root /opt/prooflane
cd /opt/prooflane
sudo python3 -m venv .venv
sudo .venv/bin/python -m pip install --cache-dir /opt/prooflane/.cache/pip -r requirements.lock
sudo docker build -t prooflane-sandbox:local sandbox
sudo install -d -o prooflane -g prooflane -m 0700 /opt/prooflane/data
sudo usermod -aG docker prooflane
sudo install -o root -g prooflane -m 0640 .env.example /opt/prooflane/.env
sudoedit /opt/prooflane/.env
```

Группа `docker` имеет root-level полномочия. Это осознанная остаточная граница текущего прототипа, а не ограниченная capability. Dedicated VM снижает последствия, но не устраняет риск. [Docker post-install](https://docs.docker.com/engine/install/linux-postinstall/).

В `.env` выставить:

```dotenv
PROOFLANE_PUBLIC_ORIGIN=https://YOUR_REAL_DOMAIN
PROOFLANE_DATA_DIR=/opt/prooflane/data
PROOFLANE_SANDBOX_IMAGE=prooflane-sandbox:local
PROOFLANE_LIVE_ENABLED=false
VULTR_INFERENCE_API_KEY=
VULTR_MODEL=
PROOFLANE_OPERATOR_TOKEN=
```

Заполнить секреты через редактор, не помещать их в shell history/аргументы команд. Начать с live=false. Для live нужен отдельный длинный случайный operator token, действующий VSI key и доступный chat model. Изменение `.env` требует restart. Secret values никогда не фиксируются в evidence.

## Сервис и HTTPS

Service example запускает один Uvicorn worker на loopback. Не увеличивать число workers без изменения общего limiter/очереди. Файлы исходников остаются root-owned; `prooflane` пишет только data и временные файлы, однако доступ к Docker всё равно привилегирован.

```sh
sudo install -o root -g root -m 0644 deploy/prooflane.service /etc/systemd/system/prooflane.service
sudo systemd-analyze verify /etc/systemd/system/prooflane.service
sudo systemctl daemon-reload
sudo systemctl enable --now prooflane
curl --fail http://127.0.0.1:8765/api/health
```

Caddy: заменить reserved `prooflane.example.com` из `deploy/Caddyfile.example` на реальный hostname. Для новой VM без другой конфигурации установить файл; для уже работающего Caddy добавить site block после проверки существующего config, не перезаписывать его:

```sh
sudoedit /etc/caddy/Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

При правильных DNS, доступности 80/443 и конфигурации Caddy управляет HTTPS. Выпуск сертификата и доступность домена здесь **NOT_RUN**. [Reverse proxy](https://caddyserver.com/docs/quick-starts/reverse-proxy), [systemd guidance](https://caddyserver.com/docs/running).

`PROOFLANE_PUBLIC_ORIGIN` должен в точности совпадать с браузерным scheme/hostname/port. Иначе POST будет отвергнут. Backend доверяет forwarded headers только от loopback Caddy; публичный доступ непосредственно к Uvicorn не нужен.

## Приёмка до публичного judging

1. Из `/opt/prooflane` чистой Linux-установки: `sudo -u prooflane env PROOFLANE_LIVE_ENABLED=false .venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/prooflane-pytest`. Service user имеет доступ к своему data directory; исходники остаются root-owned. Сохранить Python/OS/dependency versions и результат. Локальный чистый Debian/Python3.13 container уже прошёл38 tests (artifacts/linux-tests.txt); это не заменяет gate на конкретной VM. Явный --basetemp нужен, потому что source/cache root-owned.
2. Реальный sandbox smoke от пользователя `prooflane`. Скрипт пишет в `artifacts`, поэтому подготовить именно этот каталог, не передавать ему владение всем приложением:

```sh
sudo install -d -o prooflane -g prooflane -m 0700 /opt/prooflane/artifacts
sudo -u prooflane /opt/prooflane/.venv/bin/python /opt/prooflane/scripts/smoke_sandbox.py
```

3. Внешний браузер, без авторской сессии: открыть HTTPS URL, загрузить sample, выполнить sandbox, посмотреть 24/6/USD1480.00, скачать receipt, запустить offline verifier.
   Дополнительно повторить независимый corpus через `python scripts/evaluate_csv.py --base-url https://YOUR_REAL_DOMAIN --output artifacts/evaluation-cloud.json`. Ожидается 24/24; этот прогон проверяет reference/fixed-recipe и не вызывает AI. Ожидаемые числа и ограничения: [evaluation corpus](../examples/evaluation/README.md). Он не заменяет шаг 5 с настоящим VSI.
4. Проверить закрытые TCP ports и отсутствие чужих mounts/secrets; проверить, что другая браузерная сессия не читает чужой run. Сохранить несекретные evidence.
5. Включить live=true только в разрешённом бюджете, restart сервиса и провести настоящий VSI run с operator token. `python scripts/smoke_vultr.py --base-url https://45.76.92.198` проверяет публичный HTTPS, запускает один вымышленный кейс, сохраняет проверенный пакет и фиксирует ID генерации и объяснения. Скрипт запрашивает operator token без эха, если он не задан в окружении. После этого повторить путь в браузере и открыть **Proof → Baseline execution, code and receipt**.
6. Повторить на изменённом синтетическом CSV. Записать containment moment в видео с видимым режимом. Проверить GitHub/demo/video/PDF ссылки без авторизации.

Квоты приложения ограничивают число запусков, а Vultr считает вызовы по токенам. В запуске возможны генерация, одна коррекция и один запрос объяснения. Квота приложения сбрасывается при перезапуске и не задаёт лимит счёта. Контролировать расход в аккаунте. После hackathon отдельно принять решение о сохранении/удалении облачных ресурсов; остановка процесса сама по себе не означает прекращение облачных начислений.

## Диагностика и rollback

```sh
sudo systemctl status prooflane --no-pager
sudo journalctl -u prooflane -n 80 --no-pager
sudo -u prooflane docker info --format '{{.OSType}}'
sudo -u prooflane docker image inspect prooflane-sandbox:local --format '{{.Id}}'
```

Не публиковать полный журнал без проверки на входные данные/секреты. Типичные причины: daemon не запущен; не собран образ; service user не имеет Docker доступа; неверный origin; неверный VSI model/key; DNS/HTTPS ещё не готовы. Missing Docker — отказ выполнения, не fallback на host.

**Sandbox quarantined:** неподтверждённый cleanup либо контейнеры предыдущего процесса с label `prooflane.sandbox=true` блокируют новые sandbox-задачи. Состояние сохраняется в `/opt/prooflane/data/sandbox-quarantine.json` (или другом выбранном data directory), поэтому обычный restart не снимает карантин. Оператор останавливает сервис, читает marker и выполняет `sudo docker ps -a --filter label=prooflane.sandbox=true`; затем инспектирует каждый указанный exact container ID и удаляет только подтверждённые остатки этого проекта. После устранения причины и проверки, что остатков больше нет, удалить **конкретный marker** и перезапустить сервис. Не удалять marker до устранения проблемы и не использовать глобальный prune. Локальные тесты failure/restart/orphan gate прошли в составе 38 тестов; реальный crash/SIGKILL эксперимент пока NOT_RUN и должен проверяться отдельно на выделенной тестовой VM.

Перед обновлением сохранить предыдущий source revision, image ID и копию SQLite через штатный backup при остановленном app. При сбое остановить service, восстановить предыдущие source/lock/образ и совместимую БД, затем повторить smoke. Не выполнять массовый Docker prune. Схема БД проста и миграционного механизма пока нет; несовместимые изменения требуют отдельного плана.
