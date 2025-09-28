import json
from typing import List, Dict, Any


def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает JSON-файл и возвращает список словарей с данными о транзакциях.

    Args:
        file_path: Путь к JSON-файлу

    Returns:
        Список словарей с данными о транзакциях. Если файл пустой, содержит не список
        или не найден, возвращается пустой список.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Проверяем, что данные являются списком
        if isinstance(data, list):
            return data
        else:
            return []

    except (FileNotFoundError, json.JSONDecodeError):
        return []
    except Exception:
        return []