import json
import logging
from typing import List, Dict, Any
from .logger_config import setup_logger

# Создаем логгер для модуля utils
logger = setup_logger('utils', 'utils.log')


def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает JSON-файл и возвращает список словарей с данными о транзакциях.

    Args:
        file_path: Путь к JSON-файлу

    Returns:
        Список словарей с данными о транзакциях. Если файл пустой, содержит не список
        или не найден, возвращается пустой список.
    """
    logger.debug(f"Попытка чтения JSON файла: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Проверяем, что данные являются списком
        if isinstance(data, list):
            logger.info(f"Успешно прочитан JSON файл: {file_path}. Найдено {len(data)} записей")
            return data
        else:
            logger.warning(f"Файл {file_path} не содержит список. Возвращен пустой список")
            return []

    except FileNotFoundError:
        logger.error(f"Файл не найден: {file_path}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON в файле {file_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Неожиданная ошибка при чтении файла {file_path}: {e}")
        return []