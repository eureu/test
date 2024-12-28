from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import requests
import asyncio
from threading import Thread
import socket
import uuid
import os

# Конфигурация
OLLAMA_API_URL = "http://ollama:11434/api"  # Замените <ollama_port> на порт Ollama
MAIN_NODE_URL = "http://18.215.145.73:5001"  # URL main node для регистрации

# Хранение известных моделей
known_models = set()

app = FastAPI()

def get_ollama_models():
    """Получить список моделей из Ollama."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags")
        response.raise_for_status()
        return response.json().get("models", [])
    except requests.RequestException as e:
        print(f"Ошибка при запросе моделей из Ollama: {e}")
        return []

def register_with_main_node():
    """Зарегистрировать эту child node на main node."""
    try:
        # Генерация уникального ID для ноды
        # node_id = os.getenv("NODE_ID", str(uuid.uuid4()))
        node_id = os.getenv("NODE_ID")
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        # Сбор списка моделей и ресурсов
        models = get_ollama_models()
        known_models.update(models)


        # resources = {
        #     "cpu": "4 cores",  # Пример, заменить реальными данными
        #     "memory": "8GB"  # Пример, заменить реальными данными
        # }

        # Формирование payload
        payload = {
            "node_id": node_id,
            "status": "active",
            "resources": {},
            "models": models,
            "ip": ip_address,
        }

        response = requests.post(f"{MAIN_NODE_URL}/register", json=payload)
        response.raise_for_status()
        print(f"Успешно зарегистрировано на main node. Ваш node_id = {node_id}")
    except requests.RequestException as e:
        print(f"Ошибка при регистрации на main node: {e}")

# def send_ip_to_main_node():
#     """Отправить текущий IP-адрес на main node и обновить информацию в базе данных."""
#     try:
#         hostname = socket.gethostname()
#         ip_address = socket.gethostbyname(hostname)

#         # Отправить IP-адрес на main node
#         payload = {"ip_address": ip_address}
#         response = requests.post(f"{MAIN_NODE_URL}/ip", json=payload)
#         response.raise_for_status()
#         print(f"IP-адрес отправлен на main node: {ip_address}")

#         # Обновить запись в базе данных main node
#         update_payload = {"node_address": "http://localhost:<child_node_port>", "ip_address": ip_address}
#         db_response = requests.put(f"{MAIN_NODE_URL}/update_node", json=update_payload)
#         db_response.raise_for_status()
#         print(f"IP-адрес обновлен в базе данных main node: {ip_address}")
#     except requests.RequestException as e:
#         print(f"Ошибка при отправке IP-адреса на main node: {e}")
#     except socket.error as e:
#         print(f"Ошибка получения IP-адреса: {e}")

async def check_new_models():
    """Проверять Ollama на новые модели каждые 10 секунд."""
    while True:
        current_models = set(get_ollama_models())
        new_models = current_models - known_models

        if new_models:
            known_models.update(new_models)
            try:
                payload = { 
                            "node_id": os.getenv("NODE_ID"),
                             "models": list(new_models)
                          }
                response = requests.post(f"{MAIN_NODE_URL}/register", json=payload)
                response.raise_for_status()
                print(f"Новые модели отправлены на main node: {new_models}")
            except requests.RequestException as e:
                print(f"Ошибка при отправке новых моделей на main node: {e}")

        await asyncio.sleep(10)

@app.post("/api")
async def handle_client_request(request: Request):
    """Перенаправлять запросы клиента в Ollama."""
    try:
        client_payload = await request.json()

        endpoint = client_payload.endpoint
        data = client_payload.data

        response = requests.post(f"{OLLAMA_API_URL}/{endpoint}", json=data)
        response.raise_for_status()
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при запросе к Ollama: {e}")

@app.on_event("startup")
async def startup_event():
    """Регистрация и запуск проверки новых моделей при старте приложения."""
    register_with_main_node()
    # send_ip_to_main_node()
    asyncio.create_task(check_new_models())