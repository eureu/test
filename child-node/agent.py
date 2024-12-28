import os
import requests
import logging
from monitor_models import monitor_ollama_models, get_ollama_models

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MAIN_NODE_URL = os.getenv("MAIN_NODE_URL", "http://18.215.145.73:5001")
NODE_ID = os.getenv("NODE_ID", f"child_node_{os.urandom(4).hex()}")

def register_with_main_node():
    data = {
        "node_id": NODE_ID,
        "status": "active",
        "models": list(get_ollama_models())
    }
    try:
        response = requests.post(f"{MAIN_NODE_URL}/register", json=data)
        response.raise_for_status()
        logging.info("Successfully registered with Main Node.")
    except requests.RequestException as e:
        logging.error(f"Failed to register with Main Node: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during registration: {e}")

if __name__ == "__main__":
    register_with_main_node()
    monitor_ollama_models()
