from datetime import datetime
from typing import Any, Dict, List


def mask_account_card(account_info: str) -> str:
    """Маскирует номер карты или счета."""
    if not account_info or not isinstance(account_info, str):
        return account_info or ""

    # Если вся строка состоит из 16 цифр
    if account_info.isdigit() and len(account_info) == 16:
        return f"{account_info[:4]} {account_info[4:6]}** **** {account_info[-4:]}"

    parts = account_info.split()
    if not parts:
        return account_info

    number_part = parts[-1]
    if not number_part.isdigit():
        return account_info

    name_part = " ".join(parts[:-1])

    if name_part:
        if any(keyword in name_part.lower() for keyword in ["счет", "account"]):
            if len(number_part) >= 4:
                return f"{name_part} **{number_part[-4:]}"
            return account_info
        else:
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
    """Преобразует дату."""
    if not date_string or not isinstance(date_string, str):
        return ""

    try:
        clean_date = date_string.replace("Z", "+00:00")
        date_object = datetime.fromisoformat(clean_date)
        return date_object.strftime("%d.%m.%Y")
    except (ValueError, TypeError):
        return date_string


def get_transaction_amount(transaction: Dict[str, Any]) -> tuple:
    """Извлекает сумму и валюту из транзакции с поддержкой разных форматов."""
    # Пробуем разные форматы
    amount = "0.00"
    currency = ""

    # Формат 1: operationAmount как словарь
    operation_amount = transaction.get("operationAmount")
    if isinstance(operation_amount, dict):
        amount = operation_amount.get("amount", "0.00")
        currency_info = operation_amount.get("currency", {})
        if isinstance(currency_info, dict):
            currency = currency_info.get("name", currency_info.get("code", ""))
        else:
            currency = str(currency_info)

    # Формат 2: прямые поля amount и currency
    elif "amount" in transaction:
        amount = transaction.get("amount", "0.00")
        currency = transaction.get("currency", "")

    # Формат 3: поля с префиксами
    elif "operationamount" in transaction:
        if isinstance(transaction["operationamount"], dict):
            amount = transaction["operationamount"].get("amount", "0.00")
            currency_info = transaction["operationamount"].get("currency", {})
            if isinstance(currency_info, dict):
                currency = currency_info.get("name", currency_info.get("code", ""))
            else:
                currency = str(currency_info)

    # Форматируем сумму
    try:
        # Убираем возможные пробелы и лишние символы
        amount_str = str(amount).strip().replace(',', '.')
        amount = f"{float(amount_str):.2f}"
    except (ValueError, TypeError):
        amount = str(amount)

    return amount, currency


def display_transactions(transactions: List[Dict[str, Any]]) -> None:
    """Отображает список транзакций."""
    if not transactions:
        print("Не найдено транзакций, подходящих под условия фильтрации")
        return

    print(f"Всего банковских операций в выборке: {len(transactions)}\n")

    for i, transaction in enumerate(transactions, 1):
        # Форматируем дату
        date_str = transaction.get("date", "")
        formatted_date = get_date(date_str)

        description = transaction.get("description", "")
        from_account = transaction.get("from", "")
        to_account = transaction.get("to", "")

        # Получаем сумму и валюту
        amount, currency = get_transaction_amount(transaction)

        # Выводим информацию
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