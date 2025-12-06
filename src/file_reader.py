from typing import Any, Dict, List
import pandas as pd
from .logger_config import setup_logger

logger = setup_logger("file_reader", "file_reader.log")


def read_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает CSV-файл и преобразует в формат, совместимый с JSON-структурой.
    """
    logger.debug(f"Попытка чтения CSV файла: {file_path}")

    try:
        # Читаем CSV с указанием кодировки
        df = pd.read_csv(file_path, encoding='utf-8')

        # Логируем информацию о файле для отладки
        logger.debug(f"CSV файл прочитан. Колонки: {list(df.columns)}")
        logger.debug(f"Первые строки:\n{df.head()}")

        # Преобразуем DataFrame в список словарей
        transactions = df.to_dict("records")

        # Преобразуем структуру к совместимому формату
        formatted_transactions = []
        for transaction in transactions:
            formatted_transaction = {}

            # Преобразуем колонки к нужному формату
            for key, value in transaction.items():
                # Приводим ключи к нижнему регистру для consistency
                key_lower = key.lower().strip()

                if pd.isna(value):
                    formatted_transaction[key_lower] = None
                elif key_lower in ['amount', 'sum']:
                    # Для сумм преобразуем к строке с двумя знаками
                    try:
                        formatted_transaction[key_lower] = f"{float(value):.2f}"
                    except:
                        formatted_transaction[key_lower] = str(value)
                elif key_lower == 'operationamount':
                    # Если есть колонка operationAmount как строка
                    try:
                        import json
                        formatted_transaction[key_lower] = json.loads(str(value))
                    except:
                        formatted_transaction[key_lower] = str(value)
                else:
                    formatted_transaction[key_lower] = str(value)

            # Проверяем наличие обязательных полей и создаем структуру как в JSON
            if 'operationamount' not in formatted_transaction:
                # Создаем структуру operationAmount из отдельных полей
                operation_amount = {
                    "amount": formatted_transaction.get('amount', '0.00'),
                    "currency": {
                        "code": formatted_transaction.get('currency_code', 'RUB'),
                        "name": formatted_transaction.get('currency_name', 'руб.')
                    }
                }
                formatted_transaction['operationamount'] = operation_amount

            formatted_transactions.append(formatted_transaction)

        logger.info(f"Успешно прочитан CSV файл: {file_path}. Найдено {len(formatted_transactions)} записей")
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
        logger.error(traceback.format_exc())
        return []


def read_excel_file(file_path: str, sheet_name: str = 0) -> List[Dict[str, Any]]:
    """
    Читает Excel-файл и преобразует в формат, совместимый с JSON-структурой.
    """
    logger.debug(f"Попытка чтения Excel файла: {file_path}, лист: {sheet_name}")

    try:
        # Читаем Excel файл
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Логируем информацию о файле для отладки
        logger.debug(f"Excel файл прочитан. Колонки: {list(df.columns)}")
        logger.debug(f"Первые строки:\n{df.head()}")

        # Преобразуем DataFrame в список словарей
        transactions = df.to_dict("records")

        # Преобразуем структуру к совместимому формату
        formatted_transactions = []
        for transaction in transactions:
            formatted_transaction = {}

            for key, value in transaction.items():
                # Приводим ключи к нижнему регистру
                key_lower = str(key).lower().strip()

                if pd.isna(value):
                    formatted_transaction[key_lower] = None
                elif key_lower in ['amount', 'sum', 'operationamount.amount']:
                    # Для сумм преобразуем к строке с двумя знаками
                    try:
                        formatted_transaction[key_lower] = f"{float(value):.2f}"
                    except:
                        formatted_transaction[key_lower] = str(value)
                elif key_lower in ['currency', 'currency.code', 'currency.name']:
                    formatted_transaction[key_lower] = str(value)
                else:
                    formatted_transaction[key_lower] = str(value) if not pd.isna(value) else None

            # Создаем структуру operationAmount
            operation_amount = {
                "amount": formatted_transaction.get('amount',
                                                    formatted_transaction.get('operationamount.amount', '0.00')),
                "currency": {
                    "code": formatted_transaction.get('currency.code',
                                                      formatted_transaction.get('currency', 'RUB')),
                    "name": formatted_transaction.get('currency.name',
                                                      formatted_transaction.get('currency', 'руб.'))
                }
            }
            formatted_transaction['operationamount'] = operation_amount

            # Удаляем временные поля
            for field in ['amount', 'currency', 'currency.code', 'currency.name', 'operationamount.amount']:
                if field in formatted_transaction:
                    del formatted_transaction[field]

            formatted_transactions.append(formatted_transaction)

        logger.info(f"Успешно прочитан Excel файл: {file_path}. Найдено {len(formatted_transactions)} записей")
        return formatted_transactions

    except FileNotFoundError:
        logger.error(f"Excel файл не найден: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Ошибка при чтении Excel файла {file_path}: {e}")
        import traceback
        logger.error(traceback.format_exc())
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
        return read_csv_file(file_path)
    elif file_path.lower().endswith((".xlsx", ".xls")):
        return read_excel_file(file_path)
    elif file_path.lower().endswith(".json"):
        return read_json_file(file_path)
    else:
        logger.error(f"Неподдерживаемый формат файла: {file_path}")
        return []from typing import Any, Dict, List
import pandas as pd
from .logger_config import setup_logger

logger = setup_logger("file_reader", "file_reader.log")


def read_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает CSV-файл и преобразует в формат, совместимый с JSON-структурой.
    """
    logger.debug(f"Попытка чтения CSV файла: {file_path}")

    try:
        # Читаем CSV с указанием кодировки
        df = pd.read_csv(file_path, encoding='utf-8')

        # Логируем информацию о файле для отладки
        logger.debug(f"CSV файл прочитан. Колонки: {list(df.columns)}")
        logger.debug(f"Первые строки:\n{df.head()}")

        # Преобразуем DataFrame в список словарей
        transactions = df.to_dict("records")

        # Преобразуем структуру к совместимому формату
        formatted_transactions = []
        for transaction in transactions:
            formatted_transaction = {}

            # Преобразуем колонки к нужному формату
            for key, value in transaction.items():
                # Приводим ключи к нижнему регистру для consistency
                key_lower = key.lower().strip()

                if pd.isna(value):
                    formatted_transaction[key_lower] = None
                elif key_lower in ['amount', 'sum']:
                    # Для сумм преобразуем к строке с двумя знаками
                    try:
                        formatted_transaction[key_lower] = f"{float(value):.2f}"
                    except:
                        formatted_transaction[key_lower] = str(value)
                elif key_lower == 'operationamount':
                    # Если есть колонка operationAmount как строка
                    try:
                        import json
                        formatted_transaction[key_lower] = json.loads(str(value))
                    except:
                        formatted_transaction[key_lower] = str(value)
                else:
                    formatted_transaction[key_lower] = str(value)

            # Проверяем наличие обязательных полей и создаем структуру как в JSON
            if 'operationamount' not in formatted_transaction:
                # Создаем структуру operationAmount из отдельных полей
                operation_amount = {
                    "amount": formatted_transaction.get('amount', '0.00'),
                    "currency": {
                        "code": formatted_transaction.get('currency_code', 'RUB'),
                        "name": formatted_transaction.get('currency_name', 'руб.')
                    }
                }
                formatted_transaction['operationamount'] = operation_amount

            formatted_transactions.append(formatted_transaction)

        logger.info(f"Успешно прочитан CSV файл: {file_path}. Найдено {len(formatted_transactions)} записей")
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
        logger.error(traceback.format_exc())
        return []


def read_excel_file(file_path: str, sheet_name: str = 0) -> List[Dict[str, Any]]:
    """
    Читает Excel-файл и преобразует в формат, совместимый с JSON-структурой.
    """
    logger.debug(f"Попытка чтения Excel файла: {file_path}, лист: {sheet_name}")

    try:
        # Читаем Excel файл
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Логируем информацию о файле для отладки
        logger.debug(f"Excel файл прочитан. Колонки: {list(df.columns)}")
        logger.debug(f"Первые строки:\n{df.head()}")

        # Преобразуем DataFrame в список словарей
        transactions = df.to_dict("records")

        # Преобразуем структуру к совместимому формату
        formatted_transactions = []
        for transaction in transactions:
            formatted_transaction = {}

            for key, value in transaction.items():
                # Приводим ключи к нижнему регистру
                key_lower = str(key).lower().strip()

                if pd.isna(value):
                    formatted_transaction[key_lower] = None
                elif key_lower in ['amount', 'sum', 'operationamount.amount']:
                    # Для сумм преобразуем к строке с двумя знаками
                    try:
                        formatted_transaction[key_lower] = f"{float(value):.2f}"
                    except:
                        formatted_transaction[key_lower] = str(value)
                elif key_lower in ['currency', 'currency.code', 'currency.name']:
                    formatted_transaction[key_lower] = str(value)
                else:
                    formatted_transaction[key_lower] = str(value) if not pd.isna(value) else None

            # Создаем структуру operationAmount
            operation_amount = {
                "amount": formatted_transaction.get('amount',
                            formatted_transaction.get('operationamount.amount', '0.00')),
                "currency": {
                    "code": formatted_transaction.get('currency.code',
                              formatted_transaction.get('currency', 'RUB')),
                    "name": formatted_transaction.get('currency.name',
                              formatted_transaction.get('currency', 'руб.'))
                }
            }
            formatted_transaction['operationamount'] = operation_amount

            # Удаляем временные поля
            for field in ['amount', 'currency', 'currency.code', 'currency.name', 'operationamount.amount']:
                if field in formatted_transaction:
                    del formatted_transaction[field]

            formatted_transactions.append(formatted_transaction)

        logger.info(f"Успешно прочитан Excel файл: {file_path}. Найдено {len(formatted_transactions)} записей")
        return formatted_transactions

    except FileNotFoundError:
        logger.error(f"Excel файл не найден: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Ошибка при чтении Excel файла {file_path}: {e}")
        import traceback
        logger.error(traceback.format_exc())
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
        return read_csv_file(file_path)
    elif file_path.lower().endswith((".xlsx", ".xls")):
        return read_excel_file(file_path)
    elif file_path.lower().endswith(".json"):
        return read_json_file(file_path)
    else:
        logger.error(f"Неподдерживаемый формат файла: {file_path}")
        return []