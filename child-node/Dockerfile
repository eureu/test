# FROM python:3.9-slim

# WORKDIR /app

# COPY . .

# RUN pip install --no-cache-dir requests fastapi

# CMD ["python", "agent.py"]


FROM python:3.9-slim
WORKDIR /app
# COPY requirements.txt requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir requests fastapi
COPY main.py .
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD [ "python", "main.py" ]
