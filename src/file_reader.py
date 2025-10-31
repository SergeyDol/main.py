from typing import Any, Dict, List

import pandas as pd

from .logger_config import setup_logger

# Создаем логгер для модуля file_reader
logger = setup_logger("file_reader", "file_reader.log")


def read_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает CSV-файл и возвращает список словарей с данными о транзакциях.

    Args:
        file_path: Путь к CSV-файлу

    Returns:
        Список словарей с данными о транзакциях. Если файл не найден или произошла ошибка,
        возвращается пустой список.
    """
    logger.debug(f"Попытка чтения CSV файла: {file_path}")

    try:
        # Читаем CSV файл с помощью pandas
        df = pd.read_csv(file_path)

        # Конвертируем DataFrame в список словарей
        transactions = df.to_dict("records")

        logger.info(f"Успешно прочитан CSV файл: {file_path}. Найдено {len(transactions)} записей")
        return transactions

    except FileNotFoundError:
        logger.error(f"CSV файл не найден: {file_path}")
        return []
    except pd.errors.EmptyDataError:
        logger.error(f"CSV файл пустой: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Ошибка при чтении CSV файла {file_path}: {e}")
        return []


def read_excel_file(file_path: str, sheet_name: str = 0) -> List[Dict[str, Any]]:
    """
    Читает Excel-файл и возвращает список словарей с данными о транзакциях.

    Args:
        file_path: Путь к Excel-файлу
        sheet_name: Название или индекс листа (по умолчанию первый лист)

    Returns:
        Список словарей с данными о транзакциях. Если файл не найден или произошла ошибка,
        возвращается пустой список.
    """
    logger.debug(f"Попытка чтения Excel файла: {file_path}, лист: {sheet_name}")

    try:
        # Читаем Excel файл с помощью pandas
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Конвертируем DataFrame в список словарей
        transactions = df.to_dict("records")

        logger.info(f"Успешно прочитан Excel файл: {file_path}. Найдено {len(transactions)} записей")
        return transactions

    except FileNotFoundError:
        logger.error(f"Excel файл не найден: {file_path}")
        return []
    except ValueError as e:
        logger.error(f"Ошибка листа в Excel файле {file_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Ошибка при чтении Excel файла {file_path}: {e}")
        return []


def detect_file_type_and_read(file_path: str) -> List[Dict[str, Any]]:
    """
    Определяет тип файла и читает данные соответствующим способом.

    Args:
        file_path: Путь к файлу

    Returns:
        Список словарей с данными о транзакциях
    """
    logger.debug(f"Определение типа файла: {file_path}")

    if file_path.lower().endswith(".csv"):
        return read_csv_file(file_path)
    elif file_path.lower().endswith((".xlsx", ".xls")):
        return read_excel_file(file_path)
    elif file_path.lower().endswith(".json"):
        from .utils import read_json_file

        return read_json_file(file_path)
    else:
        logger.error(f"Неподдерживаемый формат файла: {file_path}")
        return []
