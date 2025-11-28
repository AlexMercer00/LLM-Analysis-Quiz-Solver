FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

COPY . .

# Install uv package manager
RUN pip install uv

# Install dependencies from pyproject.toml
RUN uv sync --frozen

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

EXPOSE 7860

CMD ["uv", "run", "main.py"]
