import json
import re
from collections import Counter
from typing import Any, Dict, List

import pandas as pd

from .logger_config import setup_logger

# Создаем логгер для модуля utils
logger = setup_logger("utils", "utils.log")


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
        with open(file_path, "r", encoding="utf-8") as file:
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


def load_csv_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает транзакции из CSV-файла с использованием pandas.

    Args:
        file_path: Путь к CSV-файлу

    Returns:
        List[Dict[str, Any]]: Список транзакций в виде словарей
    """
    logger.debug(f"Загрузка CSV транзакций из: {file_path}")

    try:
        # Читаем CSV файл с помощью pandas
        df = pd.read_csv(file_path)

        # Преобразуем DataFrame в список словарей
        transactions = df.to_dict("records")

        logger.info(f"Успешно загружено {len(transactions)} транзакций из CSV файла")
        return transactions

    except FileNotFoundError:
        logger.error(f"Файл не найден: {file_path}")
        return []
    except pd.errors.EmptyDataError:
        logger.error(f"Файл {file_path} пустой")
        return []
    except Exception as e:
        logger.error(f"Ошибка загрузки CSV-файла {file_path}: {e}")
        return []


def load_excel_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает транзакции из Excel-файла с использованием pandas.

    Args:
        file_path: Путь к Excel-файлу

    Returns:
        List[Dict[str, Any]]: Список транзакций в виде словарей
    """
    logger.debug(f"Загрузка Excel транзакций из: {file_path}")

    try:
        # Читаем Excel файл с помощью pandas
        df = pd.read_excel(file_path)

        # Преобразуем DataFrame в список словарей
        transactions = df.to_dict("records")

        logger.info(f"Успешно загружено {len(transactions)} транзакций из Excel файла")
        return transactions

    except FileNotFoundError:
        logger.error(f"Файл не найден: {file_path}")
        return []
    except pd.errors.EmptyDataError:
        logger.error(f"Файл {file_path} пустой")
        return []
    except Exception as e:
        logger.error(f"Ошибка загрузки Excel-файла {file_path}: {e}")
        return []


def process_bank_search(data: List[Dict[str, Any]], search: str) -> List[Dict[str, Any]]:
    """
    Ищет транзакции по заданной строке в описании с использованием регулярных выражений.

    Args:
        data: Список словарей с данными о банковских операциях
        search: Строка для поиска в описании операций

    Returns:
        List[Dict[str, Any]]: Список словарей с операциями, у которых в описании есть искомая строка
    """
    logger.debug(f"Поиск транзакций по строке: '{search}'")

    if not data or not search:
        logger.warning("Пустые данные или строка поиска")
        return []

    result = []
    pattern = re.compile(re.escape(search), re.IGNORECASE)

    for transaction in data:
        description = transaction.get("description", "")
        if pattern.search(description):
            result.append(transaction)

    logger.info(f"Найдено {len(result)} транзакций по запросу '{search}'")
    return result


def process_bank_operations(data: List[Dict[str, Any]], categories: List[str]) -> Dict[str, int]:
    """
    Подсчитывает количество банковских операций по категориям.

    Args:
        data: Список словарей с данными о банковских операциях
        categories: Список категорий операций для подсчета

    Returns:
        Dict[str, int]: Словарь с количеством операций по категориям
    """
    logger.debug(f"Подсчет операций по категориям: {categories}")

    if not data or not categories:
        logger.warning("Пустые данные или категории")
        return {}

    # Приводим категории к нижнему регистру для сравнения без учета регистра
    categories_lower = [cat.lower() for cat in categories]

    # Собираем все описания
    descriptions = []
    for transaction in data:
        description = transaction.get("description", "").lower()
        if description:
            descriptions.append(description)

    # Фильтруем описания по категориям
    filtered_descriptions = []
    for desc in descriptions:
        for category in categories_lower:
            if category in desc:
                filtered_descriptions.append(category)
                break

    # Используем Counter для подсчета
    counter = Counter(filtered_descriptions)

    # Восстанавливаем оригинальные названия категорий
    result = {}
    for category in categories:
        result[category] = counter.get(category.lower(), 0)

    logger.info(f"Результат подсчета операций: {result}")
    return result
