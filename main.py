import os
from typing import Any, Dict, List, Optional

from src.file_reader import detect_file_type_and_read
from src.widget import (
    display_transactions,
    filter_by_state,
    filter_rub_transactions,
    search_transactions_by_description,
    sort_transactions_by_date
)
from src.external_api import convert_amount_to_rub
from src.logger_config import setup_logger

# Создаем логгер для основного модуля
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
    """Возвращает путь к файлу в соответствии с заданием."""
    file_paths = {
        "1": "data/operations.json",  # Из предыдущих заданий
        "2": "data/transactions.csv",  # CSV файл
        "3": "data/transactions.xlsx"  # Excel файл
    }

    file_path = file_paths[choice]

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден.")

    return file_path


def get_filter_state() -> str:
    """Получает статус для фильтрации от пользователя."""
    print("\nВведите статус, по которому необходимо выполнить фильтрацию.")
    print("Доступные для фильтрации статусы: EXECUTED, CANCELED, PENDING")

    while True:
        state = input("Статус: ").strip().upper()
        if state in ["EXECUTED", "CANCELED", "PENDING"]:
            return state
        print("Неверный статус. Пожалуйста, введите EXECUTED, CANCELED или PENDING.")


def get_yes_no_input(prompt: str) -> bool:
    """Получает ответ Да/Нет от пользователя."""
    while True:
        answer = input(prompt).strip().lower()
        if answer in ["да", "д", "yes", "y"]:
            return True
        elif answer in ["нет", "н", "no", "n"]:
            return False
        print('Пожалуйста, введите "Да" или "Нет"')


def get_search_term() -> Optional[str]:
    """Получает поисковый запрос от пользователя."""
    if get_yes_no_input("Отфильтровать список транзакций по определенному слову в описании? Да/Нет: "):
        return input("Введите слово для поиска в описании: ").strip()
    return None


def process_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Обрабатывает транзакции согласно выбору пользователя."""
    if not transactions:
        return []

    # Фильтрация по статусу
    state = get_filter_state()
    filtered_transactions = filter_by_state(transactions, state)
    logger.info(f"Операции отфильтрованы по статусу '{state}', найдено {len(filtered_transactions)} транзакций")

    # Сортировка по дате
    if get_yes_no_input("Отсортировать операции по дате? Да/Нет: "):
        reverse = get_yes_no_input("Сортировать по убыванию (новые сначала)? Да/Нет: ")
        filtered_transactions = sort_transactions_by_date(filtered_transactions, reverse)
        logger.info("Операции отсортированы по дате")

    # Фильтрация рублевых транзакций
    if get_yes_no_input("Выводить только рублевые транзакции? Да/Нет: "):
        filtered_transactions = filter_rub_transactions(filtered_transactions)
        logger.info("Выводятся только рублевые транзакции")

    # Поиск по описанию
    search_term = get_search_term()
    if search_term:
        filtered_transactions = search_transactions_by_description(filtered_transactions, search_term)
        logger.info(f"Выполнен поиск по слову '{search_term}'")

    return filtered_transactions


def convert_transaction_amounts(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Конвертирует суммы транзакций в рубли."""
    converted_transactions = []

    for transaction in transactions:
        converted_transaction = transaction.copy()

        try:
            amount_rub = convert_amount_to_rub(transaction)

            # Обновляем информацию о сумме
            if "operationAmount" in converted_transaction:
                converted_transaction["operationAmount"]["amount"] = f"{amount_rub:.2f}"
                converted_transaction["operationAmount"]["currency"] = {"code": "RUB", "name": "руб."}
            else:
                converted_transaction["amount"] = f"{amount_rub:.2f}"
                converted_transaction["currency"] = "RUB"

        except Exception as e:
            logger.warning(f"Не удалось конвертировать сумму для транзакции: {e}")

        converted_transactions.append(converted_transaction)

    return converted_transactions


def main():
    """Основная функция программы."""
    try:
        # Получаем выбор файла
        choice = get_file_choice()
        file_path = get_file_path(choice)

        file_types = {"1": "JSON", "2": "CSV", "3": "XLSX"}
        print(f"\nДля обработки выбран {file_types[choice]}-файл.")

        # Читаем транзакции из файла
        transactions = detect_file_type_and_read(file_path)

        if not transactions:
            print("Не удалось прочитать транзакции из файла или файл пуст.")
            return

        # Обрабатываем транзакции
        processed_transactions = process_transactions(transactions)

        # Конвертируем суммы в рубли если нужно
        if get_yes_no_input("Конвертировать все суммы в рубли? Да/Нет: "):
            processed_transactions = convert_transaction_amounts(processed_transactions)

        # Выводим результат
        print("\nРаспечатываю итоговый список транзакций...")
        display_transactions(processed_transactions)

    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()