import os
from typing import List, Dict, Any

from .file_reader import detect_file_type_and_read
from .masks import get_mask_card_number, get_mask_account
from .utils import process_bank_search, process_bank_operations
from .external_api import convert_amount_to_rub


def filter_by_status(transactions: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции по статусу.

    Args:
        transactions: Список транзакций
        status: Статус для фильтрации

    Returns:
        Отфильтрованный список транзакций
    """
    status_lower = status.lower()
    return [t for t in transactions if t.get("state", "").lower() == status_lower]


def sort_transactions(transactions: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
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


def filter_rub_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Фильтрует рублевые транзакции.

    Args:
        transactions: Список транзакций

    Returns:
        Список рублевых транзакций
    """
    rub_transactions = []
    for transaction in transactions:
        try:
            operation_amount = transaction.get("operationAmount", {})
            currency_code = operation_amount.get("currency", {}).get("code", "")
            if currency_code == "RUB":
                rub_transactions.append(transaction)
        except (AttributeError, KeyError):
            continue
    return rub_transactions


def format_transaction(transaction: Dict[str, Any]) -> str:
    """
    Форматирует транзакцию для вывода.

    Args:
        transaction: Словарь с данными транзакции

    Returns:
        Отформатированная строка
    """
    # Форматируем дату
    date = transaction.get("date", "")[:10]

    # Описание
    description = transaction.get("description", "")

    # От и кому
    from_info = transaction.get("from", "")
    to_info = transaction.get("to", "")

    # Маскируем номера
    if from_info:
        if "счет" in from_info.lower() or "счёт" in from_info.lower() or "account" in from_info.lower():
            account_number = "".join([ch for ch in from_info if ch.isdigit()])
            from_info = f"Счет {get_mask_account(account_number)}"
        else:
            card_number = "".join([ch for ch in from_info if ch.isdigit()])
            if len(card_number) == 16:
                from_info = f"{from_info.split()[0]} {get_mask_card_number(card_number)}"

    if to_info:
        if "счет" in to_info.lower() or "счёт" in to_info.lower() or "account" in to_info.lower():
            account_number = "".join([ch for ch in to_info if ch.isdigit()])
            to_info = f"Счет {get_mask_account(account_number)}"
        else:
            card_number = "".join([ch for ch in to_info if ch.isdigit()])
            if len(card_number) == 16:
                to_info = f"{to_info.split()[0]} {get_mask_card_number(card_number)}"

    # Сумма и валюта
    operation_amount = transaction.get("operationAmount", {})
    amount = operation_amount.get("amount", "0")
    currency = operation_amount.get("currency", {}).get("name", "")

    # Формируем строку
    result = f"{date} {description}\n"
    if from_info and to_info:
        result += f"{from_info} -> {to_info}\n"
    elif from_info:
        result += f"{from_info}\n"
    elif to_info:
        result += f"{to_info}\n"

    # Конвертируем в рубли если нужно
    try:
        amount_rub = convert_amount_to_rub(transaction)
        result += f"Сумма: {amount_rub:.2f} руб.\n"
    except:
        result += f"Сумма: {amount} {currency}\n"

    return result


def main():
    """Основная функция программы."""
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    choice = input().strip()

    file_type = ""
    if choice == "1":
        file_type = "JSON"
        print("Для обработки выбран JSON-файл.")
        file_path = input("Введите путь к JSON-файлу: ").strip()
    elif choice == "2":
        file_type = "CSV"
        print("Для обработки выбран CSV-файл.")
        file_path = input("Введите путь к CSV-файлу: ").strip()
    elif choice == "3":
        file_type = "XLSX"
        print("Для обработки выбран XLSX-файл.")
        file_path = input("Введите путь к XLSX-файлу: ").strip()
    else:
        print("Неверный выбор.")
        return

    # Чтение файла
    transactions = detect_file_type_and_read(file_path)
    if not transactions:
        print(f"Не удалось прочитать файл {file_path} или файл пуст.")
        return

    # Фильтрация по статусу
    available_statuses = ["EXECUTED", "CANCELED", "PENDING"]
    while True:
        print("\nВведите статус, по которому необходимо выполнить фильтрацию.")
        print(f"Доступные для фильтровки статусы: {', '.join(available_statuses)}")
        status = input().strip().upper()

        if status in available_statuses:
            filtered_transactions = filter_by_status(transactions, status)
            print(f"Операции отфильтрованы по статусу '{status}'")
            break
        else:
            print(f"Статус операции '{status}' недоступен.")

    # Сортировка по дате
    sort_choice = input("\nОтсортировать операции по дате? Да/Нет: ").strip().lower()
    if sort_choice in ["да", "д", "yes", "y"]:
        sort_order = input("Отсортировать по возрастанию или по убыванию? ").strip().lower()
        reverse = sort_order in ["по убыванию", "убыванию", "убывание", "desc", "reverse"]
        filtered_transactions = sort_transactions(filtered_transactions, reverse)

    # Фильтрация рублевых транзакций
    rub_choice = input("\nВыводить только рублевые транзакции? Да/Нет: ").strip().lower()
    if rub_choice in ["да", "д", "yes", "y"]:
        filtered_transactions = filter_rub_transactions(filtered_transactions)

    # Поиск по описанию
    search_choice = input(
        "\nОтфильтровать список транзакций по определенному слову в описании? Да/Нет: ").strip().lower()
    if search_choice in ["да", "д", "yes", "y"]:
        search_word = input("Введите слово для поиска: ").strip()
        if search_word:
            filtered_transactions = process_bank_search(filtered_transactions, search_word)

    # Вывод результатов
    print("\nРаспечатываю итоговый список транзакций...")
    print(f"Всего банковских операций в выборке: {len(filtered_transactions)}\n")

    if not filtered_transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
    else:
        for transaction in filtered_transactions:
            print(format_transaction(transaction))
            print()


if __name__ == "__main__":
    main()