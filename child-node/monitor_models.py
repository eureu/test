import os
import subprocess
import json
import requests
import time

# MAIN_NODE_URL = "http://<main_node_ip>:<port>/register_model"
MAIN_NODE_URL = os.getenv("MAIN_NODE_URL")
# OLLAMA_CONTAINER_NAME = "ollama_container"
OLLAMA_CONTAINER_NAME = os.getenv("OLLAMA_CONTAINER_NAME")


def get_ollama_models():
    """Заходит в контейнер с Ollama, выполняет команду `ollama list` и возвращает список моделей."""
    try:
        result = subprocess.run([
            "docker", "exec", OLLAMA_CONTAINER_NAME, "ollama", "list"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error running `ollama list` in container: {result.stderr}")
            return []
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error fetching model list from container: {e}")
        return []


def notify_main_node(new_models):
    """Отправляет список новых моделей на Main Node."""
    for model in new_models:
        payload = {"model_name": model}
        try:
            response = requests.post(MAIN_NODE_URL, json=payload)
            if response.status_code == 200:
                print(f"Model {model} registered successfully with Main Node.")
            else:
                print(f"Failed to register model {model}. Response: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error notifying Main Node about model {model}: {e}")


def monitor_ollama_models():
    """Мониторит изменения в списке моделей Ollama."""
    previous_models = set()

    while True:
        current_models = set(get_ollama_models())

        if current_models != previous_models:
            # Определяем новые модели
            new_models = current_models - previous_models

            if new_models:
                print(f"New models detected: {new_models}")
                notify_main_node(new_models)

            # Можно также обработать удалённые модели, если нужно
            removed_models = previous_models - current_models
            if removed_models:
                print(f"Models removed: {removed_models}")

        previous_models = current_models
        time.sleep(10)  # Проверяем каждые 10 секунд


if __name__ == "__main__":
    monitor_ollama_models()
