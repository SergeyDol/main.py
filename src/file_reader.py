from typing import Any, Dict, List
import pandas as pd
from .logger_config import setup_logger

logger = setup_logger("file_reader", "file_reader.log")


def read_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает CSV-файл с разделителем ";" и преобразует в нужный формат.
    """
    logger.debug(f"Попытка чтения CSV файла: {file_path}")

    try:
        # Читаем CSV с разделителем ";" и кодировкой UTF-8
        df = pd.read_csv(file_path, sep=";", encoding='utf-8')

        # Логируем информацию о файле для отладки
        logger.debug(f"CSV файл прочитан. Колонки: {list(df.columns)}")
        logger.debug(f"Всего строк: {len(df)}")

        if not df.empty:
            logger.debug(f"Первые строки:\n{df.head(3)}")
            logger.debug(
                f"Уникальные статусы: {df['state'].unique() if 'state' in df.columns else 'Нет колонки state'}")

        # Заменяем NaN на None для корректной конвертации
        df = df.where(pd.notna(df), None)

        # Конвертируем DataFrame в список словарей
        transactions = df.to_dict("records")

        # Проверяем и преобразуем структуру если нужно
        formatted_transactions = []
        for transaction in transactions:
            # Приводим ключи к нижнему регистру для consistency
            formatted_transaction = {}
            for key, value in transaction.items():
                key_lower = str(key).lower().strip()

                # Особое внимание к полю state - приводим к верхнему регистру
                if key_lower == 'state' and value:
                    formatted_transaction[key_lower] = str(value).upper()
                else:
                    formatted_transaction[key_lower] = value

            # Проверяем наличие поля state
            if 'state' not in formatted_transaction:
                # Пробуем найти поле с другим названием
                state_keys = [k for k in formatted_transaction.keys() if 'state' in k.lower() or 'status' in k.lower()]
                if state_keys:
                    for state_key in state_keys:
                        if formatted_transaction[state_key]:
                            formatted_transaction['state'] = str(formatted_transaction[state_key]).upper()
                            break

            formatted_transactions.append(formatted_transaction)

        logger.info(f"Успешно прочитан CSV файл: {file_path}. Найдено {len(formatted_transactions)} записей")

        if formatted_transactions:
            logger.debug(f"Пример первой транзакции: {formatted_transactions[0]}")

        return formatted_transactions

    except FileNotFoundError:
        logger.error(f"CSV файл не найден: {file_path}")
        return []
    except pd.errors.EmptyDataError:
        logger.error(f"CSV файл пустой: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Ошибка при чтении CSV файла {file_path}: {e}")
        import traceback
        logger.error(f"Трассировка: {traceback.format_exc()}")
        return []


def read_excel_file(file_path: str, sheet_name: str = 0) -> List[Dict[str, Any]]:
    """
    Читает Excel-файл и преобразует в нужный формат.
    """
    logger.debug(f"Попытка чтения Excel файла: {file_path}, лист: {sheet_name}")

    try:
        # Читаем Excel файл
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Логируем информацию о файле
        logger.debug(f"Excel файл прочитан. Колонки: {list(df.columns)}")

        # Заменяем NaN на None
        df = df.where(pd.notna(df), None)

        # Конвертируем в список словарей
        transactions = df.to_dict("records")

        # Форматируем транзакции
        formatted_transactions = []
        for transaction in transactions:
            formatted_transaction = {}
            for key, value in transaction.items():
                key_lower = str(key).lower().strip()

                # Приводим state к верхнему регистру
                if key_lower == 'state' and value:
                    formatted_transaction[key_lower] = str(value).upper()
                else:
                    formatted_transaction[key_lower] = value

            formatted_transactions.append(formatted_transaction)

        logger.info(f"Успешно прочитан Excel файл: {file_path}. Найдено {len(formatted_transactions)} записей")
        return formatted_transactions

    except FileNotFoundError:
        logger.error(f"Excel файл не найден: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Ошибка при чтении Excel файла {file_path}: {e}")
        return []


def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """Читает JSON-файл."""
    import json

    logger.debug(f"Попытка чтения JSON файла: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            logger.info(f"Успешно прочитан JSON файл: {file_path}. Найдено {len(data)} записей")
            return data
        else:
            logger.warning(f"Файл {file_path} не содержит список.")
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
    """Определяет тип файла и читает данные."""
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