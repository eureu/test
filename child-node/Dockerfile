FROM python:3.9-slim

# Установка рабочей директории
WORKDIR /app

# Копирование только Python-файлов
COPY agent.py .

# Установка зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends docker.io docker-compose && \
    pip install --no-cache-dir requests && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Определение команды запуска
CMD ["python", "agent.py"]
