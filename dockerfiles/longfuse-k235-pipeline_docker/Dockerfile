FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir pandas

COPY longFuse/longfuse_k235_pipeline.py /app/longfuse_k235_pipeline.py

ENTRYPOINT ["python", "/app/longfuse_k235_pipeline.py"]
