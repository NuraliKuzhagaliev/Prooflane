# Deploying and operating Prooflane on Vultr

The existing public deployment is [https://45.76.92.198/](https://45.76.92.198/), Frankfurt. The root serves the product landing page; [`/app`](https://45.76.92.198/app) serves the existing review workspace. Vultr Serverless Inference is enabled and has completed real browser runs. Do not repeat first-install instructions over that installation. The later landing release adds static files and a separate workspace route, with backups and a restart of only the Prooflane service. It does not change secrets, data, sandbox settings or infrastructure.

## Existing installation

The application is `/opt/prooflane`, service `prooflane`, with a dedicated `prooflane` service account. Administrative SSH login is separate (`linuxuser`). Caddy terminates HTTPS; Uvicorn listens at `127.0.0.1:8765`. The source and environment file remain root-owned, with limited service read access. Data is writable by the service. Docker group access is privileged and requires a dedicated VM.

Configure secrets using an editor on the server, never chat, command arguments or screenshots:

```sh
sudoedit /opt/prooflane/.env
```

Required names are `VULTR_INFERENCE_API_KEY`, an available `VULTR_MODEL`, a separate random `PROOFLANE_OPERATOR_TOKEN`, and `PROOFLANE_LIVE_ENABLED=true` to explicitly authorize live calls. The browser receives only the operator token from an authorized operator; the provider key never leaves the server. Changing the environment requires `sudo systemctl restart prooflane`.

```sh
sudo systemctl status prooflane --no-pager
sudo journalctl -u prooflane -n 80 --no-pager
curl --fail http://127.0.0.1:8765/api/health
sudo -u prooflane docker image inspect prooflane-sandbox:local --format '{{.Id}}'
```

Review logs privately before sharing: they may contain source data. Public health exposes readiness, not keys. Test HTTPS with normal certificate verification; do not bypass browser warnings.

## A new dedicated VM

A VM is a cloud computer, not a download. Check current Vultr pricing, coupon coverage and credit expiry before creating resources. This repository does not create accounts, enable billing or purchase servers. A 2-vCPU / 2–4-GB Linux CPU VM is a starting engineering estimate, not a measured capacity guarantee; no GPU is needed.

Prepare a separate Ed25519 SSH key with a passphrase, without overwriting an existing key. Add only its `.pub` contents to Vultr SSH Keys and select it when creating the VM. Keep the private file local. Verify the host fingerprint through the trusted console before accepting it. Limited User Login controls administrative login; it does not control whether visitors can view the website.

Use an OS supported by the chosen Python and Docker packages. Python 3.13 is the tested development version. The screenshot of the existing VM reports Ubuntu 26.10; this document does not pretend that it was created as Ubuntu 24.04. For a new server, review the current supported LTS release. Install Docker Engine, Python/venv and Caddy from their official package instructions: [Docker](https://docs.docker.com/engine/install/ubuntu/), [Caddy](https://caddyserver.com/docs/install).

Upload only a reviewed release containing `prooflane`, `web`, `sandbox`, `examples`, `scripts`, `deploy`, dependency locks and required documents. Exclude `.env`, `.git`, `.venv`, caches, databases, keys and private artifacts. Keep a release hash and previous revision/image for rollback.

On a new, confirmed dedicated installation, inspect ownership and existing accounts first. Create the `prooflane` system account if absent, root-owned `/opt/prooflane`, and a mode-0700 service-owned data directory. Create the venv, install `requirements.lock`, and build `sandbox` as `prooflane-sandbox:local`. Give the service Docker access only with awareness that it grants host-root-level power. Copy `.env.example` to a new restricted `.env` without overwriting a real configuration.

```dotenv
PROOFLANE_PUBLIC_ORIGIN=https://YOUR_REAL_HOSTNAME
PROOFLANE_DATA_DIR=/opt/prooflane/data
PROOFLANE_SANDBOX_IMAGE=prooflane-sandbox:local
PROOFLANE_LIVE_ENABLED=false
VULTR_INFERENCE_API_KEY=
VULTR_MODEL=
PROOFLANE_OPERATOR_TOKEN=
```

Start with live disabled. A VM coupon does not automatically create an inference subscription. Obtain the subscription's key and an available chat model through [Vultr's connection instructions](https://docs.vultr.com/products/compute/serverless-inference/management/connection). Review its allowance; application quotas are not billing caps.

## Service and HTTPS

Review `deploy/prooflane.service` before installing it. It uses one Uvicorn worker and loopback binding. Validate a new service with `systemd-analyze verify`, reload systemd, then start it and check local health. Do not increase workers without shared rate/concurrency controls.

Review `deploy/Caddyfile.example`. Replace the reserved hostname with one you control, or use a properly validated IP-certificate configuration as on the existing VM. Merge only the project site block into an existing Caddy configuration; never overwrite unrelated sites. Validate with `caddy validate --config /etc/caddy/Caddyfile` before reloading. [Reverse proxy](https://caddyserver.com/docs/quick-starts/reverse-proxy).

Open only the required public HTTP/HTTPS ports for Caddy and restrict SSH to administrative access. Do not expose port 8765 or the Docker daemon. `PROOFLANE_PUBLIC_ORIGIN` must exactly match the browser's scheme/host/port; otherwise POSTs are rejected. Forwarded headers are trusted only from loopback.

## Acceptance and rollback

1. Run the Python and JavaScript regression suites in the target release. A local validation image does not prove the VM installation. Save OS, Python, lockfile and image identities.
2. Run `scripts/smoke_sandbox.py` as the service user in a specifically writable artifact directory. Confirm actual controls, bounded I/O and cleanup.
3. Check public HTTPS and the source-decision workflow. `scripts/smoke_case.py --base-url https://YOUR_HOST --output-dir artifacts/cloud` exercises Reference and Docker without model calls. `scripts/smoke_review.py --base-url https://YOUR_HOST --mode sandbox --output-dir artifacts/review` covers recovery and exports.
4. Verify cross-session denial and closed backend/daemon ports. Do not broaden firewall rules simply to make a test pass.
5. Only within an authorized allowance, enable live and run `scripts/smoke_vultr.py --base-url https://YOUR_HOST`; it requests an operator token without echo if needed. Then perform a real browser run, inspect model/request IDs, code, verifier and cleanup, and check its downloaded packet offline.
6. Record a fresh containment moment and verify public repo/demo/media access. Do not claim final LabLab submission until the platform confirms it.

Before an update, preserve the prior source revision, image ID and a consistent SQLite backup. Restore compatible source/lock/image/database if a release fails, then repeat smoke checks. A frontend-only change can be rolled back by restoring its exact saved file; no database migration is needed for the video-status fix.

Quarantine persists through restarts. Stop the app, inspect `PROOFLANE_DATA_DIR/sandbox-quarantine.json` and each exact container bearing `prooflane.sandbox=true`. Correct the cause and remove only confirmed project leftovers. Clear the specific marker only after confirming their absence. Do not use global prune. A real SIGKILL lifecycle experiment remains NOT_RUN.

After the event, the owner must decide whether to retain or delete cloud resources. Stopping a process or VM does not by itself establish that billing has stopped. No new charged resource was created during demo production.
