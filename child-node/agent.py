import os
import requests
import subprocess
import time

# Получение параметров из переменных окружения
MAIN_NODE_URL = os.getenv("MAIN_NODE_URL", "http://localhost:5001")
NODE_ID = os.getenv("NODE_ID", "child_node_1")

def register_with_main_node():
    data = {
        "node_id": NODE_ID,
        "status": "active"
    }
    try:
        response = requests.post(f"{MAIN_NODE_URL}/register", json=data)
        if response.status_code == 200:
            print("Successfully registered with Main Node")
        else:
            print(f"Failed to register: {response.json()}")
    except Exception as e:
        print(f"Error registering with Main Node: {e}")

def start_containers():
    try:
        # Запуск ollama и open-webui через docker-compose
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        print("Containers started successfully")
    except Exception as e:
        print(f"Error starting containers: {e}")

if __name__ == "__main__":
    # Шаг 1: Регистрация на Main Node
    register_with_main_node()

    # Шаг 2: Ожидание и запуск docker-compose.yml
    time.sleep(5)
    start_containers()
