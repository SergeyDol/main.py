from typing import Any, Dict, List
import pandas as pd
from .logger_config import setup_logger

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
        # Пробуем разные кодировки
        encodings = ['utf-8', 'cp1251', 'windows-1251', 'latin1']

        for encoding in encodings:
            try:
                logger.debug(f"Попытка чтения с кодировкой: {encoding}")
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            # Если ни одна кодировка не подошла
            logger.error(f"Не удалось определить кодировку CSV файла: {file_path}")
            return []

        # Логируем информацию о DataFrame для отладки
        logger.debug(f"Размер DataFrame: {df.shape}")
        logger.debug(f"Колонки DataFrame: {list(df.columns)}")

        if not df.empty:
            logger.debug(f"Первые несколько строк:\n{df.head(2)}")

        # Заменяем NaN на None для корректной конвертации в JSON
        df = df.where(pd.notna(df), None)

        # Конвертируем DataFrame в список словарей
        transactions = df.to_dict("records")

        # Дополнительная обработка для корректного отображения данных
        for transaction in transactions:
            # Преобразуем числовые значения в строки для consistency
            for key, value in transaction.items():
                if isinstance(value, (int, float)) and value is not None:
                    transaction[key] = str(value)

        logger.info(f"Успешно прочитан CSV файл: {file_path}. Найдено {len(transactions)} записей")

        if transactions:
            logger.debug(f"Пример первой транзакции: {transactions[0]}")

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
        # Читаем Excel файл
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Логируем информацию о DataFrame для отладки
        logger.debug(f"Размер DataFrame: {df.shape}")
        logger.debug(f"Колонки DataFrame: {list(df.columns)}")

        if not df.empty:
            logger.debug(f"Первые несколько строк:\n{df.head(2)}")

        # Заменяем NaN на None
        df = df.where(pd.notna(df), None)

        # Конвертируем DataFrame в список словарей
        transactions = df.to_dict("records")

        # Дополнительная обработка для корректного отображения данных
        for transaction in transactions:
            # Преобразуем числовые значения в строки, особенно суммы
            for key, value in transaction.items():
                if isinstance(value, (int, float)) and value is not None:
                    # Для полей с суммами сохраняем 2 знака после запятой
                    if 'amount' in key.lower() or 'sum' in key.lower():
                        transaction[key] = f"{value:.2f}"
                    else:
                        transaction[key] = str(value)

        logger.info(f"Успешно прочитан Excel файл: {file_path}. Найдено {len(transactions)} записей")

        if transactions:
            logger.debug(f"Пример первой транзакции: {transactions[0]}")

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


def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает JSON-файл и возвращает список словарей с данными о транзакциях.

    Args:
        file_path: Путь к JSON-файлу

    Returns:
        Список словарей с данными о транзакциях. Если файл пустой, содержит не список
        или не найден, возвращается пустой список.
    """
    import json

    logger.debug(f"Попытка чтения JSON файла: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Проверяем, что данные являются списком
        if isinstance(data, list):
            logger.info(f"Успешно прочитан JSON файл: {file_path}. Найдено {len(data)} записей")

            if data:
                logger.debug(f"Пример первой транзакции: {data[0]}")

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
        logger.debug(f"Определен как CSV файл: {file_path}")
        return read_csv_file(file_path)
    elif file_path.lower().endswith((".xlsx", ".xls")):
        logger.debug(f"Определен как Excel файл: {file_path}")
        return read_excel_file(file_path)
    elif file_path.lower().endswith(".json"):
        logger.debug(f"Определен как JSON файл: {file_path}")
        return read_json_file(file_path)
    else:
        logger.error(f"Неподдерживаемый формат файла: {file_path}")
        return []