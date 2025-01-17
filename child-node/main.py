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

OLLAMA_API_URL = "http://ollama:11434/api"
MAIN_NODE_URL = "http://18.215.145.73:5001"

known_models = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск приложения")
    register_with_main_node()
    asyncio.create_task(check_new_models())
    yield
    print("Остановка приложения")

app = FastAPI(lifespan=lifespan)

def get_ollama_models():
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags")
        response.raise_for_status()
        return response.json().get("models", [])
    except requests.RequestException as e:
        print(f"Ошибка при запросе моделей из Ollama: {e}")
        return []

def register_with_main_node():

    try:
        node_id = os.getenv("NODE_ID")
        hostname = socket.gethostname()

        ip_address = ''

        models = get_ollama_models()
        model_names = {model["name"] for model in models if "name" in model}
        known_models.update(model_names)

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


async def check_new_models():
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
    try:
        client_payload = await request.json()
        print(client_payload)
        print('-----------------')
        print(f"{OLLAMA_API_URL}/{endpoint}")

        response = requests.post(f"{OLLAMA_API_URL}/{endpoint}", json=client_payload)
        response.raise_for_status()
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при запросе к Ollama: {e}")

@app.get("/api/{endpoint:path}")
async def handle_client_get_request(endpoint: str, request: Request):
    try:

        print(request)

        response = requests.get(f"{OLLAMA_API_URL}/{endpoint}", params=request)
        response.raise_for_status()

        return JSONResponse(content=response.json(), status_code=response.status_code)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при запросе к Ollama: {e}")

@app.get("/")
async def read_root():
    return {"message": "Приложение работает!"}
