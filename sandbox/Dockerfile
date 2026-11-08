FROM python:3.13-slim-bookworm@sha256:5024f48ba9441d4b13a95d3945abc6365538e3a31109833367a1923523c6efed
COPY --chmod=0444 runner.py /opt/prooflane/runner.py
RUN chmod 0555 /opt/prooflane
USER 65534:65534
WORKDIR /tmp
ENTRYPOINT ["python", "-I", "-B", "/opt/prooflane/runner.py"]
