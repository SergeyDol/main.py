from datetime import datetime
from typing import Any, Dict, List


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

    # Определяем тип на основе названия
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
        # Если нет названия, определяем по длине номера
        if len(number_part) == 16:
            return f"{number_part[:4]} {number_part[4:6]}** **** {number_part[-4:]}"
        elif len(number_part) >= 4:
            return f"**{number_part[-4:]}"
        return account_info


def get_date(date_string: str) -> str:
    """Преобразует дату из формата 'YYYY-MM-DDThh:mm:ss.ssssss' в 'DD.MM.YYYY'."""
    if not date_string or not isinstance(date_string, str):
        return ""

    try:
        clean_date = date_string.replace("Z", "+00:00")
        date_object = datetime.fromisoformat(clean_date)
        return date_object.strftime("%d.%m.%Y")
    except (ValueError, TypeError):
        return date_string


def get_transaction_amount(transaction: Dict[str, Any]) -> tuple:
    """Извлекает сумму и валюту из транзакции."""
    operation_amount = transaction.get("operationAmount", {})

    if isinstance(operation_amount, dict):
        amount = operation_amount.get("amount", "0.00")
        currency_info = operation_amount.get("currency", {})
        if isinstance(currency_info, dict):
            currency = currency_info.get("name", "")
        else:
            currency = str(currency_info)
    else:
        amount = transaction.get("amount", "0.00")
        currency = transaction.get("currency", "")

    # Форматируем сумму
    try:
        amount = f"{float(amount):.2f}"
    except (ValueError, TypeError):
        amount = str(amount)

    return amount, currency


def display_transactions(transactions: List[Dict[str, Any]]) -> None:
    """Отображает список транзакций."""
    if not transactions:
        print("Не найдено транзакций, подходящих под условия фильтрации")
        return

    print(f"Всего банковских операций в выборке: {len(transactions)}\n")

    for transaction in transactions:
        # Форматируем дату
        date_str = transaction.get("date", "")
        formatted_date = get_date(date_str)

        description = transaction.get("description", "")
        from_account = transaction.get("from", "")
        to_account = transaction.get("to", "")

        # Получаем сумму и валюту
        amount, currency = get_transaction_amount(transaction)

        # Выводим информацию о транзакции
        print(f"{formatted_date} {description}")

        # Маскируем номера карт/счетов
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