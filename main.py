import os
from typing import Any, Dict, List

from src.file_reader import detect_file_type_and_read
from src.processing import filter_by_state, sort_by_date
from src.masks import mask_account_card, get_date
from src.external_api import convert_amount_to_rub
from src.generators import filter_by_currency
from src.logger_config import setup_logger

# Создаем логгер
logger = setup_logger("main", "main.log")


def get_file_choice() -> str:
    """Получает выбор типа файла от пользователя."""
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    while True:
        choice = input("Введите номер пункта (1-3): ").strip()
        if choice in ["1", "2", "3"]:
            return choice
        print("Неверный ввод. Пожалуйста, введите 1, 2 или 3.")


def get_file_path(choice: str) -> str:
    """Возвращает путь к файлу."""
    file_paths = {
        "1": "data/operations.json",
        "2": "data/transactions.csv",
        "3": "data/transactions.xlsx"
    }

    file_path = file_paths[choice]

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден.")

    return file_path


def get_filter_state() -> str:
    """Получает статус для фильтрации."""
    print("\nВведите статус для фильтрации (EXECUTED, CANCELED, PENDING):")

    while True:
        state = input("Статус: ").strip().upper()
        if state in ["EXECUTED", "CANCELED", "PENDING"]:
            return state
        print("Неверный статус.")


def get_yes_no_input(prompt: str) -> bool:
    """Получает ответ Да/Нет."""
    while True:
        answer = input(prompt).strip().lower()
        if answer in ["да", "д", "yes", "y"]:
            return True
        elif answer in ["нет", "н", "no", "n"]:
            return False
        print('Пожалуйста, введите "Да" или "Нет"')


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


def main():
    """Основная функция программы."""
    try:
        # Выбор файла
        choice = get_file_choice()
        file_path = get_file_path(choice)

        file_types = {"1": "JSON", "2": "CSV", "3": "XLSX"}
        print(f"\nОбработка {file_types[choice]}-файла...")

        # Чтение транзакций
        transactions = detect_file_type_and_read(file_path)

        if not transactions:
            print("Не удалось прочитать транзакции из файла.")
            return

        # Фильтрация по статусу
        state = get_filter_state()
        filtered_transactions = filter_by_state(transactions, state)
        logger.info(f"Фильтрация по статусу '{state}': {len(filtered_transactions)} транзакций")

        # Сортировка по дате
        if get_yes_no_input("Отсортировать операции по дате? Да/Нет: "):
            reverse = get_yes_no_input("По убыванию (новые сначала)? Да/Нет: ")
            filtered_transactions = sort_by_date(filtered_transactions, reverse)
            logger.info("Операции отсортированы по дате")

        # Фильтрация рублевых транзакций
        if get_yes_no_input("Выводить только рублевые транзакции? Да/Нет: "):
            rub_transactions = list(filter_by_currency(filtered_transactions, "RUB"))
            filtered_transactions = rub_transactions
            logger.info(f"Оставлены только рублевые транзакции: {len(filtered_transactions)}")

        # Поиск по описанию
        if get_yes_no_input("Фильтровать по слову в описании? Да/Нет: "):
            search_term = input("Введите слово для поиска: ").strip()
            if search_term:
                found_transactions = [
                    t for t in filtered_transactions
                    if search_term.lower() in str(t.get("description", "")).lower()
                ]
                filtered_transactions = found_transactions
                logger.info(f"Поиск по '{search_term}': {len(filtered_transactions)} транзакций")

        # Конвертация в рубли
        if get_yes_no_input("Конвертировать все суммы в рубли? Да/Нет: "):
            for transaction in filtered_transactions:
                try:
                    amount_rub = convert_amount_to_rub(transaction)
                    if "operationAmount" in transaction:
                        transaction["operationAmount"]["amount"] = f"{amount_rub:.2f}"
                        transaction["operationAmount"]["currency"] = {"code": "RUB", "name": "руб."}
                except Exception as e:
                    logger.warning(f"Ошибка конвертации: {e}")

        # Вывод результата
        print("\nРезультат:")
        display_transactions(filtered_transactions)

    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
    except KeyboardInterrupt:
        print("\nПрограмма прервана.")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()