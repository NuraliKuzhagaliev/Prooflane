# Security boundaries

Prooflane is a bounded hackathon prototype. Passing the recorded probes is evidence of those controls in those runs, not certification that arbitrary hostile code is safe.

## Threat model

Untrusted inputs include CSV contents and filenames, user questions, model plans and Python, and container stdout/stderr. Protected assets include inference credentials, the host filesystem, other sessions' results, availability and the credit allowance. The current application, host OS, Docker daemon, pinned base image and VM administrator are trusted.

## Implemented controls

- Generated Python runs only in a disposable Docker container. Clients cannot choose images, mounts, shell arguments or runtime flags. Input travels through stdin, not a host mount.
- Before starting, Docker inspect must confirm network `none`, a read-only root, UID/GID 65534, 128 MiB memory and total memory-plus-swap, 0.5 CPU, 32 PIDs, `cap-drop ALL`, `no-new-privileges`, and no host mounts. Writable tmpfs is limited to 16 MiB. Normal execution has a 10-second deadline, 128 KiB stdout and 32 KiB stderr limits.
- Removal is checked after success, failure and timeout. Unconfirmed cleanup rejects the result and persists `sandbox-quarantine.json`. A new process also checks containers labelled `prooflane.sandbox=true`; leftovers cause quarantine. Restarting does not clear the marker.
- Inference credentials remain in the server control layer. The provider endpoint is fixed; redirects and environment-proxy inheritance are disabled. Live requests require explicit enablement and a separate operator token. No provider key is sent to a container or the browser.
- Input validation precedes execution. The independent Decimal verifier checks the exact output schema, coverage, totals and every finding. Malformed, incomplete or mismatching results are withheld. One bounded repair is permitted only after cleanup is confirmed; feedback contains neither raw CSV nor stderr.
- Runs and cases belong to a random HttpOnly/SameSite session cookie; HTTPS sets Secure. POST requests check Origin, JSON and a custom header. These browser protections are not general account authentication. Concurrency and request quotas are bounded in one server worker; headers and CSP constrain the UI context.
- Legacy scenarios bind one declared numeric change to the original receipt and owner. Cases support up to four alternatives with twelve distinct changes each, all applied jointly to the original baseline. Shared contract changes propagate to every bound row. Revision checks and a process lock prevent lost updates. Failed runs do not become completed alternatives.
- Case verification reconstructs both sources, explicit choices/exclusions, baseline context, declared changes, receipts and exact analytics. It never imports or executes packet Python. Packets are limited to 8 MiB; create/match bodies to 2 MiB; each CSV to 128 KiB and 500 records; candidate links to 5,000. These caps are not a public load-test result.

Actual live inference and Docker runs are recorded in [the live check](docs/LIVE_AI_CHECK_20261109.md) and [new demo packet](artifacts/live-demo-v2/live-case-packet.json). Five fresh containment probes passed during recording. Tests cover cleanup/restart/orphan gates with controlled doubles; a real process-SIGKILL experiment remains NOT_RUN. [Commands and distinctions](TESTING.md).

## Residual risks

Docker shares the host kernel. Kernel/daemon vulnerabilities or a configuration defect can defeat containment. Docker group membership grants root-level power even to a non-root service account; systemd hardening does not remove that power. Use a dedicated VM, keep its OS maintained, and never publish the daemon's TCP API. [Docker security](https://docs.docker.com/engine/security/) and [daemon access](https://docs.docker.com/engine/install/linux-postinstall/).

The operator token is a shared demo secret, not RBAC. Its holder can consume live allowance. In-memory quotas reset on restart and are not billing caps. Public fixed-recipe requests can create load. Wider deployment needs host quotas, monitoring, an execution broker and operational review.

SQLite and receipts contain source data. Logical retention is 24 hours, with deletion triggered by activity, not an exact background timer. Free pages and backups may retain bytes; secure erasure and application-level at-rest encryption are absent. Use fictional data on the public demo and inspect exports before sharing.

SHA-256 receipts are unsigned. An attacker can rewrite content and recompute hashes. Verification checks consistency and arithmetic, not author identity, runtime attestation, supplier authenticity, contractual liability or recovered savings. The environment probe checks one key variable's absence; it does not prove that every possible secret is absent. The network probe observes a denied connection in a network-none container, not every possible covert channel.

Raw rows are not automatically sent to the model. A user can still put sensitive information in the question, which is sent. Prompt instructions are not the containment boundary.

## Operations and reporting

Keep `.env` outside Git with restricted permissions. Never print it into logs, screenshots or a video. Revoke a leaked key at Vultr and replace the operator token. Keep Uvicorn on loopback behind HTTPS; restrict SSH separately.

For quarantine: stop the service; inspect the marker and `docker ps -a --filter label=prooflane.sandbox=true`; identify each exact project container and investigate it. Remove only confirmed project leftovers after determining the cause. Only after verifying their absence and correcting the cause should the operator remove the specific data-directory marker and restart. Do not remove the marker to bypass a fault or run global Docker prune.

Report defects with a revision, steps, synthetic reproducer and observed result through the repository's security reporting facility where available. Do not publish credentials or actual invoices. No bug bounty is claimed.
