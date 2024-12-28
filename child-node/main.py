from ipaddress import ip_address
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import requests
import asyncio
from threading import Thread
import socket
import uuid
import os
from contextlib import asynccontextmanager
import subprocess

# Конфигурация
OLLAMA_API_URL = "http://ollama:11434/api"  # Замените <ollama_port> на порт Ollama
MAIN_NODE_URL = "http://18.215.145.73:5001"  # URL main node для регистрации

# Хранение известных моделей
known_models = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Логика старта приложения
    print("Запуск приложения")
    register_with_main_node()
    asyncio.create_task(check_new_models())
    yield
    # Логика завершения приложения (при необходимости)
    print("Остановка приложения")

app = FastAPI(lifespan=lifespan)

def get_ollama_models():
    """Получить список моделей из Ollama."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags")
        response.raise_for_status()
        return response.json().get("models", [])
    except requests.RequestException as e:
        print(f"Ошибка при запросе моделей из Ollama: {e}")
        return []

# def get_host_ip():
#     # Получаем IP-адрес контейнера
#     container_ip = socket.gethostbyname(socket.gethostname())
    
#     # Получаем IP-адрес хоста через маршрут (по умолчанию это 172.17.0.1)
#     result = subprocess.run(['ip', 'route', 'show'], stdout=subprocess.PIPE)
#     route_info = result.stdout.decode('utf-8')
    
#     # Ищем строку с маршрутом по умолчанию, который указывает на IP хоста
#     for line in route_info.splitlines():
#         if 'default' in line:
#             host_ip = line.split()[2]
#             return host_ip
    
#     return container_ip  # Если не нашли, возвращаем IP контейнера

# print(get_host_ip())

def register_with_main_node():
    """Зарегистрировать эту child node на main node."""
    try:
        # Генерация уникального ID для ноды
        # node_id = os.getenv("NODE_ID", str(uuid.uuid4()))
        node_id = os.getenv("NODE_ID")
        hostname = socket.gethostname()

        # ip_address = socket.gethostbyname(hostname)
        # ip_address = get_host_ip()
        ip_address = ''

        # Сбор списка моделей и ресурсов
        models = get_ollama_models()
        model_names = {model["name"] for model in models if "name" in model}
        known_models.update(model_names)

        # resources = {
        #     "cpu": "4 cores",  # Пример, заменить реальными данными
        #     "memory": "8GB"  # Пример, заменить реальными данными
        # }

        # Формирование payload
        payload = {
            "node_id": node_id,
            "status": "active",
            "resources": {},
            "models": list(model_names),
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

@app.post("/api/{endpoint:path}")
async def handle_client_request(endpoint: str, request: Request):
    """Перенаправлять запросы клиента в Ollama."""
    try:
        client_payload = await request.json()
        print(client_payload)
        # endpoint = client_payload.endpoint
        # data = client_payload.data

        response = requests.post(f"{OLLAMA_API_URL}/{endpoint}", json=client_payload)
        response.raise_for_status()
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при запросе к Ollama: {e}")

@app.get("/api/{endpoint:path}")
async def handle_client_get_request(endpoint: str, request: Request):
    """Перенаправлять GET-запросы клиента в Ollama."""
    try:
        # Получаем параметры из запроса
        # query_params = dict(request.query_params)

        print(request)

        # Предполагаем, что клиент передает endpoint как параметр
        # endpoint = query_params.pop("endpoint", None)
        # if not endpoint:
        #     raise HTTPException(status_code=400, detail="Параметр 'endpoint' обязателен")

        # Отправляем GET-запрос на Ollama API
        response = requests.get(f"{OLLAMA_API_URL}/{endpoint}", params=request)
        response.raise_for_status()

        return JSONResponse(content=response.json(), status_code=response.status_code)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при запросе к Ollama: {e}")


# @app.on_event("startup")
# async def startup_event():
#     """Регистрация и запуск проверки новых моделей при старте приложения."""
#     register_with_main_node()
#     # send_ip_to_main_node()
#     asyncio.create_task(check_new_models())


@app.get("/")
async def read_root():
    return {"message": "Приложение работает!"}