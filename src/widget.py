from datetime import datetime
from typing import Any, Dict, List
from typing import List, Dict, Any


def filter_by_state(transactions: List[Dict[str, Any]], state: str) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции по статусу.

    Args:
        transactions: Список транзакций
        state: Статус для фильтрации

    Returns:
        Отфильтрованный список транзакций
    """
    return [t for t in transactions if t.get("state", "").upper() == state.upper()]


def sort_transactions_by_date(transactions: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
    """
    Сортирует транзакции по дате.

    Args:
        transactions: Список транзакций
        reverse: Если True - по убыванию, False - по возрастанию

    Returns:
        Отсортированный список транзакций
    """
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
        # Если есть название, проверяем ключевые слова для счета
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
    # Явная проверка на None и нестроковые значения
    if date_string is None:
        return ""

    if not isinstance(date_string, str):
        return ""

    # Проверка на пустую строку
    if not date_string.strip():
        return ""

    try:
        # Обработка даты
        clean_date = date_string.replace("Z", "+00:00")
        date_object = datetime.fromisoformat(clean_date)
        return date_object.strftime("%d.%m.%Y")
    except (ValueError, TypeError):
        # В случае ошибки возвращаем исходную строку
        return date_string


def mask_account_number(account: str) -> str:
    """
    Маскирует номер счета или карты.

    Args:
        account: Номер счета или карты

    Returns:
        str: Замаскированный номер
    """
    if not account:
        return ""

    if "счет" in account.lower():
        # Для счетов: показываем последние 4 цифры
        numbers = "".join(filter(str.isdigit, account))
        if len(numbers) >= 4:
            return f"**{numbers[-4:]}"
    else:
        # Для карт: показываем первые 6 и последние 4 цифры
        numbers = "".join(filter(str.isdigit, account))
        if len(numbers) >= 16:
            return f"{numbers[:4]} {numbers[4:6]}** **** {numbers[-4:]}"

    return account


def display_transactions(transactions: List[Dict[str, Any]]) -> None:
    """
    Отображает список транзакций в удобочитаемом формате.

    Args:
        transactions: Список транзакций для отображения
    """
    if not transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    print(f"Всего банковских операций в выборке: {len(transactions)}\n")

    for transaction in transactions:
        # Используем функцию get_date для форматирования даты
        date_str = transaction.get("date", "")
        formatted_date = get_date(date_str)

        description = transaction.get("description", "")
        from_account = transaction.get("from", "")
        to_account = transaction.get("to", "")
        amount = transaction.get("amount", "")
        currency = transaction.get("currency", "")

        print(f"{formatted_date} {description}")

        if from_account:
            # Используем mask_account_card вместо mask_account_number для лучшей обработки
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
