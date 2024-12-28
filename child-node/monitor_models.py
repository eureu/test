import subprocess
import json
import requests
import time
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MAIN_NODE_URL = os.getenv('MAIN_NODE_URL', "http://18.215.145.73:5001")
OLLAMA_CONTAINER_NAME = os.getenv('OLLAMA_CONTAINER_NAME', "ollama_default_container")
OLLAMA_API_URL = "http://ollama:11434/api/tags"


def get_ollama_models():
    try:
        response = requests.get(OLLAMA_API_URL)
        response.raise_for_status()
        data = response.json()
        
        models = [model["name"] for model in data.get("models", [])]
        logging.info(f"Retrieved models: {models}")
        return models
    except requests.RequestException as e:
        logging.error(f"Error fetching models from Ollama API: {e}")
        return []
    except KeyError as e:
        logging.error(f"Unexpected data format from Ollama API: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return []

def notify_main_node(new_models):
    payload = {"models": list(new_models)}
    try:
        response = requests.post(f'{MAIN_NODE_URL}/register-models', json=payload)
        response.raise_for_status()
        logging.info(f"Models registered successfully with Main Node: {new_models}")
    except requests.RequestException as e:
        logging.error(f"Failed to register models with Main Node: {e}")
    except Exception as e:
        logging.error(f"Unexpected error notifying Main Node about models: {e}")

def monitor_ollama_models():
    previous_models = set()

    while True:
        current_models = set(get_ollama_models())

        if current_models != previous_models:
            new_models = current_models - previous_models

            if new_models:
                logging.info(f"New models detected: {new_models}")
                notify_main_node(new_models)

            removed_models = previous_models - current_models
            if removed_models:
                logging.info(f"Models removed: {removed_models}")

        previous_models = current_models
        time.sleep(10)
