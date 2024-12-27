FROM python:3.9-slim

# Установка рабочей директории
WORKDIR /app

# Копирование только Python-файлов
COPY . .

# Установка зависимостей
RUN pip install --no-cache-dir requests 

# Определение команды запуска
CMD ["python", "agent.py"]