import os
from typing import List, Dict, Any

from src.file_reader import detect_file_type_and_read
from src.processing import filter_by_state, sort_by_date
from src.widget import mask_account_card, get_date, display_transactions
from src.generators import filter_by_currency, transaction_descriptions
from src.utils import process_bank_search, process_bank_operations


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
    """Возвращает фиксированный путь к файлу в зависимости от выбора."""
    file_paths = {
        "1": "data/operations.json",  # Путь к JSON файлу
        "2": "data/transactions.csv",  # Путь к CSV файлу
        "3": "data/transactions.xlsx"  # Путь к XLSX файлу
    }

    return file_paths[choice]


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


def main():
    """Основная функция программы."""
    try:
        # Выбор файла
        choice = get_file_choice()
        file_path = get_file_path(choice)

        file_types = {"1": "JSON", "2": "CSV", "3": "XLSX"}
        file_type = file_types[choice]
        print(f"\nОбработка {file_type}-файла...")

        # Чтение транзакций из файла
        transactions = detect_file_type_and_read(file_path)

        if not transactions:
            print(f"Не удалось прочитать транзакции из файла {file_path}")
            return

        print(f"Прочитано {len(transactions)} транзакций")

        # Фильтрация по статусу
        state = get_filter_state()
        filtered_transactions = filter_by_state(transactions, state)
        print(f"Операции отфильтрованы по статусу '{state}'")

        if not filtered_transactions:
            print(f"Нет транзакций со статусом '{state}'")
            return

        # Сортировка по дате
        if get_yes_no_input("Отсортировать операции по дате? Да/Нет: "):
            reverse = get_yes_no_input("Сортировать по убыванию (новые сначала)? Да/Нет: ")
            filtered_transactions = sort_by_date(filtered_transactions, reverse)
            print("Операции отсортированы по дате")

        # Фильтрация рублевых транзакций
        if get_yes_no_input("Выводить только рублевые транзакции? Да/Нет: "):
            rub_transactions = list(filter_by_currency(filtered_transactions, "RUB"))
            filtered_transactions = rub_transactions
            print("Выводятся только рублевые транзакции")

        # Поиск по описанию
        if get_yes_no_input("Выполнить поиск по описанию транзакций? Да/Нет: "):
            search_term = input("Введите слово для поиска: ").strip()
            if search_term:
                filtered_transactions = process_bank_search(filtered_transactions, search_term)
                print(f"Выполнен поиск по слову '{search_term}'")

        # Статистика по категориям (опционально)
        if get_yes_no_input("Показать статистику по категориям операций? Да/Нет: "):
            categories_input = input("Введите категории через запятую (например: перевод, оплата, вклад): ").strip()
            if categories_input:
                categories = [cat.strip() for cat in categories_input.split(",")]
                operations_stats = process_bank_operations(filtered_transactions, categories)
                print("\nСтатистика по операциям:")
                for category, count in operations_stats.items():
                    print(f"  {category}: {count} операций")

        # Вывод транзакций
        print("\nРезультат обработки транзакций:")
        display_transactions(filtered_transactions)

    except FileNotFoundError as e:
        print(f"Ошибка: Файл не найден - {e}")
        print("Убедитесь, что в папке 'data/' находятся файлы:")
        print("  - operations.json")
        print("  - transactions.csv")
        print("  - transactions.xlsx")
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()