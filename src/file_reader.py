from typing import Any, Dict, List
import pandas as pd
from .logger_config import setup_logger

logger = setup_logger("file_reader", "file_reader.log")


def read_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает CSV-файл и возвращает список словарей с данными о транзакциях.
    """
    logger.debug(f"Попытка чтения CSV файла: {file_path}")

    try:
        # Читаем CSV с разными возможными разделителями
        df = pd.read_csv(file_path, encoding='utf-8')

        # Заменяем NaN на None для корректной конвертации в JSON-подобный формат
        df = df.where(pd.notna(df), None)

        # Конвертируем DataFrame в список словарей
        transactions = df.to_dict("records")

        # Логируем для отладки
        if transactions:
            logger.debug(f"Колонки CSV: {list(transactions[0].keys())}")

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
    """
    logger.debug(f"Попытка чтения Excel файла: {file_path}, лист: {sheet_name}")

    try:
        # Читаем Excel файл
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Заменяем NaN на None
        df = df.where(pd.notna(df), None)

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


3.
Исправленный
widget.py
для
отображения
сумм:
python
from datetime import datetime
from typing import Any, Dict, List


def filter_by_state(transactions: List[Dict[str, Any]], state: str) -> List[Dict[str, Any]]:
    """Фильтрует транзакции по статусу."""
    if not transactions:
        return []

    filtered_transactions = []
    for t in transactions:
        transaction_state = str(t.get("state", "")).upper().strip()
        target_state = state.upper().strip()

        if transaction_state == target_state:
            filtered_transactions.append(t)

    return filtered_transactions


def sort_transactions_by_date(transactions: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
    """Сортирует транзакции по дате."""

    def get_date(transaction):
        return transaction.get("date", "")

    return sorted(transactions, key=get_date, reverse=reverse)


def mask_account_card(account_info: str) -> str:
    """Маскирует номер карты или счета в переданной строке."""
    if not account_info or not isinstance(account_info, str):
        return account_info or ""

    # Если вся строка состоит из 16 цифр - это номер карты
    if account_info.isdigit() and len(account_info) == 16:
        return f"{account_info[:4]} {account_info[4:6]}** **** {account_info[-4:]}"

    parts = account_info.split()
    if not parts:
        return account_info

    number_part = parts[-1]

    # Если последняя часть не состоит из цифр, возвращаем как есть
    if not number_part.isdigit():
        return account_info

    name_part = " ".join(parts[:-1])

    # Определяем тип на основе названия или длины номера
    if name_part:
        if any(keyword in name_part.lower() for keyword in ["счет", "account"]):
            # Это счет
            if len(number_part) >= 4:
                return f"{name_part} **{number_part[-4:]}"
            return account_info
        else:
            # Это карта
            if len(number_part) == 16:
                return f"{name_part} {number_part[:4]} {number_part[4:6]}** **** {number_part[-4:]}"
            return account_info
    else:
        if len(number_part) == 16:
            return f"{number_part[:4]} {number_part[4:6]}** **** {number_part[-4:]}"
        elif len(number_part) >= 4:
            return f"**{number_part[-4:]}"
        return account_info


def get_date(date_string: str) -> str:
    """Преобразует дату из формата 'YYYY-MM-DDThh:mm:ss.ssssss' в 'DD.MM.YYYY'."""
    if date_string is None:
        return ""

    if not isinstance(date_string, str):
        return ""

    if not date_string.strip():
        return ""

    try:
        clean_date = date_string.replace("Z", "+00:00")
        date_object = datetime.fromisoformat(clean_date)
        return date_object.strftime("%d.%m.%Y")
    except (ValueError, TypeError):
        return date_string


def get_transaction_amount(transaction: Dict[str, Any]) -> tuple:
    """Извлекает сумму и валюту из транзакции."""
    # Пробуем разные форматы данных
    operation_amount = transaction.get("operationAmount", {})

    if isinstance(operation_amount, dict):
        amount = operation_amount.get("amount")
        currency_info = operation_amount.get("currency", {})
        if isinstance(currency_info, dict):
            currency = currency_info.get("name", currency_info.get("code", ""))
        else:
            currency = str(currency_info)
    else:
        amount = transaction.get("amount")
        currency = transaction.get("currency", "")

    # Обрабатываем сумму
    if amount is None:
        amount = "0.00"
    elif isinstance(amount, (int, float)):
        amount = f"{amount:.2f}"
    else:
        amount = str(amount)

    # Обрабатываем валюту
    if not currency:
        currency = ""

    return amount, currency


def display_transactions(transactions: List[Dict[str, Any]]) -> None:
    """Отображает список транзакций в удобочитаемом формате."""
    if not transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    print(f"Всего банковских операций в выборке: {len(transactions)}\n")

    for transaction in transactions:
        # Форматируем дату
        date_str = transaction.get("date", "")
        formatted_date = get_date(date_string=date_str)

        description = transaction.get("description", "")
        from_account = transaction.get("from", "")
        to_account = transaction.get("to", "")

        # Получаем сумму и валюту
        amount, currency = get_transaction_amount(transaction)

        print(f"{formatted_date} {description}")

        if from_account:
            masked_from = mask_account_card(from_account)
            if to_account:
                masked_to = mask_account_card(to_account)
                print(f"{masked_from} -> {masked_to}")
            else:
                print(f"{masked_from}")
        elif to_account:
            masked_to = mask_account_card(to_account)
            print(f"{masked_to}")

        print(f"Сумма: {amount} {currency}\n")


def filter_rub_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Фильтрует рублевые транзакции."""
    if not transactions:
        return []

    rub_transactions = []
    for transaction in transactions:
        operation_amount = transaction.get("operationAmount", {})
        if isinstance(operation_amount, dict):
            currency = operation_amount.get("currency", {})
            if isinstance(currency, dict):
                currency_code = currency.get("code", "")
            else:
                currency_code = str(currency)
        else:
            currency_code = transaction.get("currency", "")

        if str(currency_code).upper() == "RUB":
            rub_transactions.append(transaction)

    return rub_transactions


def search_transactions_by_description(transactions: List[Dict[str, Any]], search_term: str) -> List[Dict[str, Any]]:
    """Ищет транзакции по ключевому слову в описании."""
    if not transactions or not search_term:
        return []

    found_transactions = []
    for transaction in transactions:
        description = str(transaction.get("description", "")).lower()
        if search_term.lower() in description:
            found_transactions.append(transaction)

    return found_transactions