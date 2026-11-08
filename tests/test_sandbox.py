import json
import subprocess
import sys

import pytest

from prooflane.sandbox import DockerSandbox, SandboxError, _capture_bounded, MAX_STDOUT_BYTES


def test_absent_docker_fails_closed(monkeypatch):
    monkeypatch.setattr("prooflane.sandbox.shutil.which", lambda _: None)
    sandbox = DockerSandbox()
    assert not sandbox.available()["available"]
    with pytest.raises(SandboxError, match="unavailable"):
        sandbox.run("print('must not execute')", "")


@pytest.mark.parametrize("image", ["--privileged", "bad image", "image;whoami", "", "a\n--mount"])
def test_image_reference_validation(image, monkeypatch):
    monkeypatch.setenv("PROOFLANE_SANDBOX_IMAGE", image)
    with pytest.raises(SandboxError):
        DockerSandbox()


def test_container_controls_are_fixed():
    args = DockerSandbox()._create_arguments("prooflane-" + "a" * 32)
    assert args[args.index("--network") + 1] == "none"
    assert args[args.index("--user") + 1] == "65534:65534"
    assert args[args.index("--memory") + 1] == "128m"
    assert args[args.index("--memory-swap") + 1] == "128m"
    assert args[args.index("--cap-drop") + 1] == "ALL"
    assert "no-new-privileges=true" in args and "--read-only" in args
    assert not any(a in args for a in ["--env", "-e", "--volume", "-v", "--mount", "--privileged", "--pid=host"])


def test_input_bounds_precede_any_execution(monkeypatch):
    sandbox = DockerSandbox()
    monkeypatch.setattr(sandbox, "available", lambda: pytest.fail("Docker must not be called"))
    for code, data, timeout in [("x" * 32769, "", 10), ("pass", "x" * 131073, 10), ("pass", "", 0), ("pass", "", True)]:
        with pytest.raises(SandboxError):
            sandbox.run(code, data, timeout)


def test_bounded_process_timeout():
    # Trusted test fixture only; submitted code never calls this utility directly.
    _, _, _, error = _capture_bounded([sys.executable, "-c", "import time;time.sleep(5)"], b"", 0.1)
    assert "wall-clock" in error


def test_bounded_process_output():
    output, _, _, error = _capture_bounded([sys.executable, "-c", "import sys;sys.stdout.write('x'*500000)"], b"", 3)
    assert len(output) == MAX_STDOUT_BYTES
    assert "output exceeded" in error


def test_cleanup_needs_positive_daemon_response(monkeypatch):
    sandbox = DockerSandbox()
    monkeypatch.setattr(sandbox, "_command", lambda args, **kwargs: subprocess.CompletedProcess(args, 1, b"", b"daemon unavailable"))
    assert sandbox._cleanup("prooflane-" + "a" * 32) is False


def test_unconfirmed_runtime_controls_refuse_execution_and_cleanup(monkeypatch):
    sandbox = DockerSandbox()
    calls = []
    def command(args, **kwargs):
        calls.append(args)
        if args[0] == "create":
            return subprocess.CompletedProcess(args, 0, b"a" * 64, b"")
        if args[0] == "inspect":
            return subprocess.CompletedProcess(args, 0, json.dumps({"image":"sha256:x", "user":"0", "host":{}, "mounts":[]}).encode(), b"")
        return subprocess.CompletedProcess(args, 0, b"", b"")
    monkeypatch.setattr(sandbox, "available", lambda: {"available":True})
    monkeypatch.setattr(sandbox, "_command", command)
    monkeypatch.setattr("prooflane.sandbox._capture_bounded", lambda *args: pytest.fail("Must not execute with unconfirmed controls"))
    with pytest.raises(SandboxError, match="isolation controls") as error:
        sandbox.run("print(42)", "")
    assert error.value.execution["cleanup"] is True
    assert any(c[0] == "rm" for c in calls)


def test_cleanup_failure_surfaces_in_error(monkeypatch):
    sandbox = DockerSandbox()
    monkeypatch.setattr(sandbox, "available", lambda: {"available":True})
    monkeypatch.setattr(sandbox, "_command", lambda args, **kwargs: subprocess.CompletedProcess(args, 1, b"", b""))
    monkeypatch.setattr(sandbox, "_cleanup", lambda name: False)
    with pytest.raises(SandboxError, match="cleanup could not be verified") as error:
        sandbox.run("print(42)", "")
    assert error.value.execution["cleanup"] is False
