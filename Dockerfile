FROM python:3.13.9-alpine3.22

ENV UV_NO_DEV=1
ENV UV_NO_CACHE=1

RUN pip install --no-cache-dir uv==0.9.5

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

COPY . .

CMD ["uv", "run", "main.py"]
