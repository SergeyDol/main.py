import os
from typing import Any, Dict, List, Optional

from src.file_reader import detect_file_type_and_read
from src.widget import (
    display_transactions,
    filter_by_state,
    filter_rub_transactions,
    search_transactions_by_description,
    sort_transactions_by_date,
    display_transaction_debug_info
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
    """Возвращает путь к файлу в зависимости от выбора."""
    file_paths = {
        "1": "data/transactions.json",  # Путь к JSON файлу
        "2": "data/transactions.csv",  # Путь к CSV файлу
        "3": "data/transactions.xlsx"  # Путь к XLSX файлу
    }

    file_path = file_paths[choice]

    # Проверяем существование файла
    if not os.path.exists(file_path):
        # Если файла нет в data/, пробуем найти в корне
        alt_path = file_path.replace("data/", "")
        if os.path.exists(alt_path):
            return alt_path
        else:
            raise FileNotFoundError(f"Файл {file_path} не найден. Убедитесь, что файл добавлен в проект.")

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
    print("\nОтфильтровать список транзакций по определенному слову в описании?")
    if get_yes_no_input("Да/Нет: "):
        return input("Введите слово для поиска в описании: ").strip()
    return None


def process_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Обрабатывает транзакции согласно выбору пользователя."""
    if not transactions:
        return []

    # Фильтрация по статусу
    state = get_filter_state()
    filtered_transactions = filter_by_state(transactions, state)
    print(f"Операции отфильтрованы по статусу '{state}'")

    # Для отладки - покажем что мы получили
    print(f"Найдено транзакций после фильтрации по статусу: {len(filtered_transactions)}")

    if filtered_transactions:
        display_transaction_debug_info(filtered_transactions[:1])  # Показываем только первую для отладки

    # Сортировка по дате
    print("\nОтсортировать операции по дате?")
    if get_yes_no_input("Да/Нет: "):
        reverse = get_yes_no_input("Сортировать по убыванию (новые сначала)? Да/Нет: ")
        filtered_transactions = sort_transactions_by_date(filtered_transactions, reverse)
        print("Операции отсортированы по дате")

    # Фильтрация рублевых транзакций
    print("\nВыводить только рублевые транзакции?")
    if get_yes_no_input("Да/Нет: "):
        filtered_transactions = filter_rub_transactions(filtered_transactions)
        print("Выводятся только рублевые транзакции")

    # Поиск по описанию
    search_term = get_search_term()
    if search_term:
        filtered_transactions = search_transactions_by_description(filtered_transactions, search_term)
        print(f"Выполнен поиск по слову '{search_term}'")

    return filtered_transactions


def convert_transaction_amounts(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Конвертирует суммы транзакций в рубли."""
    converted_transactions = []

    for transaction in transactions:
        # Создаем копию транзакции чтобы не изменять оригинал
        converted_transaction = transaction.copy()

        try:
            # Конвертируем сумму в рубли
            amount_rub = convert_amount_to_rub(transaction)

            # Обновляем информацию о сумме
            if "operationAmount" in converted_transaction:
                converted_transaction["operationAmount"]["amount"] = str(round(amount_rub, 2))
                converted_transaction["operationAmount"]["currency"] = {"code": "RUB", "name": "руб."}
            else:
                converted_transaction["amount"] = str(round(amount_rub, 2))
                converted_transaction["currency"] = "RUB"

        except Exception as e:
            logger.warning(f"Не удалось конвертировать сумму для транзакции {transaction.get('id', 'unknown')}: {e}")
            # Оставляем оригинальную сумму если конвертация не удалась

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

        print(f"Прочитано транзакций из файла: {len(transactions)}")

        # Обрабатываем транзакции согласно выбору пользователя
        processed_transactions = process_transactions(transactions)

        # Конвертируем суммы в рубли если нужно
        print("\nКонвертировать все суммы в рубли?")
        if get_yes_no_input("Да/Нет: "):
            processed_transactions = convert_transaction_amounts(processed_transactions)
            print("Суммы конвертированы в рубли")

        # Выводим результат
        print("\nРаспечатываю итоговый список транзакций...")
        display_transactions(processed_transactions)

    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        print("Пожалуйста, добавьте файлы транзакций в проект:")
        print("- transactions.json")
        print("- transactions.csv")
        print("- transactions.xlsx")
        print("Разместите их в папке 'data/' или в корне проекта.")
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        logger.error(f"Критическая ошибка в работе программы: {e}")
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()