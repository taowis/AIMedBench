FROM python:3.11-slim
WORKDIR /work
COPY pyproject.toml README.md /work/
RUN pip install --no-cache-dir .
COPY . /work
