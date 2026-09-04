FROM python:3.12-slim

WORKDIR /suite
COPY requirements.lock ./
RUN python -m pip install --no-cache-dir -r requirements.lock
COPY . ./

ENTRYPOINT ["python", "/suite/suite/run_conformance.py"]
