"""Disposable Docker execution. Never executes submitted Python on the host."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import threading
import time
import uuid


MAX_CODE_BYTES = 32 * 1024
MAX_CSV_BYTES = 128 * 1024
MAX_STDOUT_BYTES = 128 * 1024
MAX_STDERR_BYTES = 32 * 1024
LIMITS = {
    "network": "none", "memory_mb": 128, "cpu": 0.5, "pids": 32,
    "tmpfs_mb": 16, "read_only_root": True, "user": "65534:65534",
    "capabilities": "none", "no_new_privileges": True, "host_mounts": False,
}


class SandboxError(RuntimeError):
    def __init__(self, message: str, execution: dict | None = None):
        super().__init__(message)
        self.execution = execution or {}


def _capture_bounded(command: list[str], payload: bytes, timeout: float) -> tuple[bytes, bytes, int, str | None]:
    """Read concurrently with fixed memory caps; timeout includes writing stdin."""
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=False)
    buffers = [bytearray(), bytearray()]
    overflow = threading.Event()

    def reader(pipe, index: int, limit: int):
        try:
            while chunk := pipe.read(4096):
                remaining = max(0, limit - len(buffers[index]))
                buffers[index].extend(chunk[:remaining])
                if len(chunk) > remaining:
                    overflow.set()
        except (OSError, ValueError):
            pass
        finally:
            pipe.close()

    def writer():
        try:
            process.stdin.write(payload)
            process.stdin.close()
        except (BrokenPipeError, OSError, ValueError):
            pass

    readers = [
        threading.Thread(target=reader, args=(process.stdout, 0, MAX_STDOUT_BYTES), daemon=True),
        threading.Thread(target=reader, args=(process.stderr, 1, MAX_STDERR_BYTES), daemon=True),
    ]
    for thread in readers:
        thread.start()
    write_thread = threading.Thread(target=writer, daemon=True)
    write_thread.start()
    deadline = time.monotonic() + timeout
    failure = None
    while process.poll() is None:
        if overflow.is_set():
            failure = "Sandbox output exceeded the configured byte limit."
            break
        if time.monotonic() >= deadline:
            failure = "Sandbox exceeded its wall-clock time limit."
            break
        time.sleep(0.01)
    if process.poll() is None:
        process.kill()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
        failure = failure or "Docker client did not stop."
    for thread in readers:
        thread.join(timeout=1)
    write_thread.join(timeout=1)
    if overflow.is_set():
        failure = "Sandbox output exceeded the configured byte limit."
    return bytes(buffers[0]), bytes(buffers[1]), process.returncode or 0, failure


class DockerSandbox:
    def __init__(self, image: str | None = None):
        self.image = os.environ.get("PROOFLANE_SANDBOX_IMAGE", "prooflane-sandbox:local") if image is None else image
        if not isinstance(self.image, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/@:\-]{0,255}", self.image):
            raise SandboxError("Invalid sandbox image reference.")
        self.docker = shutil.which("docker")

    def _command(self, args: list[str], timeout: float = 8) -> subprocess.CompletedProcess:
        if not self.docker:
            raise SandboxError("Docker is not installed. Generated code cannot run.")
        try:
            return subprocess.run([self.docker, *args], capture_output=True, timeout=timeout, shell=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SandboxError("Docker is unavailable or its control operation timed out.") from exc

    def available(self) -> dict:
        try:
            engine = self._command(["version", "--format", "{{.Server.Os}}"], timeout=4)
            if engine.returncode or engine.stdout.strip() != b"linux":
                return {"available": False, "detail": "A running Linux Docker engine is required."}
            image = self._command(["image", "inspect", self.image, "--format", "{{.Id}}"], timeout=4)
            if image.returncode:
                return {"available": False, "detail": "Build the prooflane-sandbox image first."}
            return {"available": True, "detail": "Linux Docker engine and sandbox image are available."}
        except SandboxError:
            return {"available": False, "detail": "Docker is unavailable. No generated code will run."}

    def stale_containers(self) -> list[str]:
        """Startup-only inventory; caller must never invoke this during active jobs."""
        result = self._command(["container", "ls", "--all", "--filter", "label=prooflane.sandbox=true", "--format", "{{.ID}}"])
        if result.returncode:
            raise SandboxError("Cannot verify absence of containers from an earlier service run.")
        return result.stdout.decode("ascii", errors="replace").split()

    def _create_arguments(self, name: str) -> list[str]:
        if not re.fullmatch(r"prooflane-[0-9a-f]{32}", name):
            raise SandboxError("Invalid internal sandbox name.")
        return [
            "create", "--name", name, "--label", "prooflane.sandbox=true", "--interactive",
            "--init", "--network", "none", "--read-only", "--user", "65534:65534",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges=true",
            "--memory", "128m", "--memory-swap", "128m", "--cpus", "0.5",
            "--pids-limit", "32", "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=16m,mode=1777",
            "--ulimit", "fsize=1048576:1048576", "--ulimit", "nofile=64:64",
            "--log-driver", "none", "--stop-timeout", "1", self.image,
        ]

    def _cleanup(self, name: str) -> bool:
        try:
            self._command(["rm", "--force", name])
            # A successful list + absent exact name proves removal. A failed inspect alone cannot.
            found = self._command(["container", "ls", "--all", "--filter", f"name=^/{name}$", "--format", "{{.ID}}"])
            return found.returncode == 0 and not found.stdout.strip()
        except SandboxError:
            return False

    def run(self, code: str, csv_text: str, timeout: int = 10) -> dict:
        if not isinstance(code, str) or not code.strip() or len(code.encode("utf-8")) > MAX_CODE_BYTES:
            raise SandboxError("Python code must contain between 1 and 32768 UTF-8 bytes.")
        if not isinstance(csv_text, str) or len(csv_text.encode("utf-8")) > MAX_CSV_BYTES:
            raise SandboxError("CSV input exceeds 128 KiB.")
        if type(timeout) is not int or not 1 <= timeout <= 30:
            raise SandboxError("Sandbox timeout must be an integer between 1 and 30 seconds.")
        readiness = self.available()
        if not readiness["available"]:
            raise SandboxError(readiness["detail"])
        name = "prooflane-" + uuid.uuid4().hex
        started = time.monotonic()
        result = {"stdout": "", "stderr": "", "exit_code": -1, "container_id": "",
                  "image_id": "", "cleanup": False, "runtime": "Docker / Python",
                  "limits": {**LIMITS, "timeout_seconds": timeout,
                             "stdout_bytes": MAX_STDOUT_BYTES, "stderr_bytes": MAX_STDERR_BYTES}}
        failure = None
        try:
            created = self._command(self._create_arguments(name))
            if created.returncode:
                raise SandboxError("Docker could not create the isolated environment.")
            container_id = created.stdout.decode("ascii", errors="replace").strip()
            if not re.fullmatch(r"[0-9a-f]{64}", container_id):
                raise SandboxError("Docker returned an invalid container identifier.")
            result["container_id"] = container_id
            metadata = self._command(["inspect", "--format",
                '{"image":{{json .Image}},"user":{{json .Config.User}},"host":{{json .HostConfig}},"mounts":{{json .Mounts}}}', name])
            if metadata.returncode:
                raise SandboxError("Could not inspect the sandbox image identity.")
            inspected = json.loads(metadata.stdout)
            host = inspected["host"]
            observed = {
                "network": host.get("NetworkMode"), "read_only_root": host.get("ReadonlyRootfs"),
                "user": inspected.get("user"), "memory_bytes": host.get("Memory"),
                "memory_swap_bytes": host.get("MemorySwap"), "nano_cpus": host.get("NanoCpus"),
                "pids": host.get("PidsLimit"), "cap_drop": host.get("CapDrop"),
                "security_options": host.get("SecurityOpt"),
                "host_mount_count": sum(m.get("Type") != "tmpfs" for m in inspected.get("mounts", [])),
            }
            isolated = (observed["network"] == "none" and observed["read_only_root"] is True
                        and observed["user"] == "65534:65534"
                        and observed["memory_bytes"] == 128 * 1024 * 1024
                        and observed["memory_swap_bytes"] == 128 * 1024 * 1024
                        and observed["nano_cpus"] == 500000000 and observed["pids"] == 32
                        and observed["cap_drop"] == ["ALL"]
                        and "no-new-privileges=true" in (observed["security_options"] or [])
                        and observed["host_mount_count"] == 0)
            result["observed_controls"] = observed
            if not isolated:
                raise SandboxError("Docker did not confirm the required isolation controls. Execution refused.")
            result["image_id"] = inspected["image"]
            payload = json.dumps({"code": code, "csv": csv_text}, ensure_ascii=False).encode("utf-8")
            stdout, stderr, exit_code, failure = _capture_bounded(
                [self.docker, "start", "--attach", "--interactive", name], payload, timeout)
            result.update(stdout=stdout.decode("utf-8", errors="replace"),
                          stderr=stderr.decode("utf-8", errors="replace"), exit_code=exit_code)
            if not failure:
                state = self._command(["inspect", "--format", "{{.State.Running}} {{.State.ExitCode}} {{.State.OOMKilled}}", name])
                parts = state.stdout.decode("ascii", errors="replace").strip().split()
                if state.returncode or len(parts) != 3 or parts[0] != "false":
                    failure = "Sandbox did not report a completed process."
                else:
                    result["exit_code"] = int(parts[1])
                    result["oom_killed"] = parts[2] == "true"
        except (SandboxError, OSError, ValueError, KeyError, TypeError) as exc:
            failure = str(exc) if isinstance(exc, SandboxError) else "Sandbox execution failed."
        finally:
            result["cleanup"] = self._cleanup(name)
            result["elapsed_ms"] = round((time.monotonic() - started) * 1000, 2)
        if not result["cleanup"]:
            failure = "Sandbox cleanup could not be verified. Stop further runs and inspect Docker."
        if failure:
            raise SandboxError(failure, execution=result)
        return result

    def probe(self) -> dict:
        code = '''import json, os, socket
checks = []
try:
    with socket.create_connection(("192.0.2.1", 443), timeout=1):
        checks.append({"name":"Network egress", "passed":False, "detail":"Unexpected connection to the documentation IP."})
except OSError:
    checks.append({"name":"Network egress", "passed":True, "detail":"Connection to 192.0.2.1:443 failed inside this network-none container."})
try:
    with open("/prooflane-write-probe", "w") as target:
        target.write("probe")
    checks.append({"name":"Root filesystem", "passed":False, "detail":"Unexpected root filesystem write."})
except OSError:
    checks.append({"name":"Root filesystem", "passed":True, "detail":"Writing /prooflane-write-probe was denied."})
checks.append({"name":"Inference credential", "passed":"VULTR_INFERENCE_API_KEY" not in os.environ, "detail":"Checks only that the inference key variable is absent; no secret values are read."})
checks.append({"name":"Non-root identity", "passed":os.getuid() == 65534, "detail":"Effective user ID: " + str(os.getuid())})
print(json.dumps({"checks":checks}))
'''
        execution = self.run(code, "", timeout=8)
        try:
            payload = json.loads(execution["stdout"])
            checks = payload["checks"]
        except (ValueError, KeyError, TypeError) as exc:
            raise SandboxError("Containment probe did not produce valid evidence.", execution) from exc
        checks.append({"name": "Lifecycle cleanup", "passed": execution["cleanup"],
                       "detail": "Container absence checked after force removal."})
        return {"passed": execution["exit_code"] == 0 and all(c["passed"] for c in checks),
                "checks": checks, "execution": execution}
