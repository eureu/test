import os
import requests
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Получение параметров из переменных окружения
MAIN_NODE_URL = os.getenv("MAIN_NODE_URL", "http://18.215.145.73:5001")
NODE_ID = os.getenv("NODE_ID", "child_node_1") # рандомный ID сделать в перспективе

def register_with_main_node():
    """
    Регистрирует текущий узел на основном узле.
    """
    data = {
        "node_id": NODE_ID,
        "status": "active"
    }
    try:
        response = requests.post(f"{MAIN_NODE_URL}/register", json=data)
        if response.status_code == 200:
            logging.info("Successfully registered with Main Node.")
        else:
            logging.error(f"Failed to register: {response.json()}")
    except Exception as e:
        logging.error(f"Error registering with Main Node: {e}")

if __name__ == "__main__":
    register_with_main_node()
