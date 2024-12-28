FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir requests fastapi uvicorn

COPY main.py .

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
