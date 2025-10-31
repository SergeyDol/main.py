from typing import Any, Dict, List

from widgets.transaction_widgets import display_transactions

from utils.file_operations import load_csv_transactions, load_excel_transactions, load_json_transactions
from utils.transaction_operations import process_bank_operations, process_bank_search


def filter_by_status(transactions: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции по статусу.

    Args:
        transactions: Список транзакций
        status: Статус для фильтрации

    Returns:
        List[Dict[str, Any]]: Отфильтрованный список транзакций
    """
    if not transactions:
        return []

    status_lower = status.lower()
    filtered = []

    for transaction in transactions:
        transaction_status = transaction.get("status", "").lower()
        if transaction_status == status_lower:
            filtered.append(transaction)

    return filtered


def sort_transactions(transactions: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
    """
    Сортирует транзакции по дате.

    Args:
        transactions: Список транзакций
        reverse: Если True - сортировка по убыванию, иначе по возрастанию

    Returns:
        List[Dict[str, Any]]: Отсортированный список транзакций
    """
    return sorted(transactions, key=lambda x: x.get("date", ""), reverse=reverse)


def filter_rub_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Фильтрует рублевые транзакции.

    Args:
        transactions: Список транзакций

    Returns:
        List[Dict[str, Any]]: Список рублевых транзакций
    """
    if not transactions:
        return []

    return [
        transaction
        for transaction in transactions
        if transaction.get("currency", "").lower() in ["rub", "руб", "рубль", "rur"]
    ]


def get_user_choice(prompt: str, valid_choices: List[str]) -> str:
    """
    Получает выбор пользователя с валидацией.

    Args:
        prompt: Сообщение для пользователя
        valid_choices: Список допустимых ответов

    Returns:
        str: Выбор пользователя
    """
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid_choices:
            return choice
        print(f"Некорректный ввод. Допустимые варианты: {', '.join(valid_choices)}")


def main() -> None:
    """
    Основная функция программы, реализующая пользовательский интерфейс.
    Связывает все функциональности проекта между собой.
    """
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    file_choice = input("Ваш выбор: ").strip()

    transactions = []
    file_type = ""

    if file_choice == "1":
        file_type = "JSON"
        file_path = input("Введите путь к JSON-файлу: ").strip()
        transactions = load_json_transactions(file_path)
        print("Для обработки выбран JSON-файл.")

    elif file_choice == "2":
        file_type = "CSV"
        file_path = input("Введите путь к CSV-файлу: ").strip()
        transactions = load_csv_transactions(file_path)
        print("Для обработки выбран CSV-файл.")

    elif file_choice == "3":
        file_type = "XLSX"
        file_path = input("Введите путь к XLSX-файлу: ").strip()
        transactions = load_excel_transactions(file_path)  # Изменено на load_excel_transactions
        print("Для обработки выбран XLSX-файл.")

    else:
        print("Некорректный выбор файла.")
        return

    if not transactions:
        print(f"Не удалось загрузить транзакции из {file_type}-файла.")
        return

    # Фильтрация по статусу
    available_statuses = ["EXECUTED", "CANCELED", "PENDING"]

    while True:
        print("\nВведите статус, по которому необходимо выполнить фильтрацию.")
        print(f"Доступные для фильтровки статусы: {', '.join(available_statuses)}")
        status = input("Статус: ").strip().upper()

        if status in available_statuses:
            filtered_transactions = filter_by_status(transactions, status)
            print(f'Операции отфильтрованы по статусу "{status}"')
            break
        else:
            print(f'Статус операции "{status}" недоступен.')

    if not filtered_transactions:
        print("Не найдено транзакций с выбранным статусом.")
        return

    # Сортировка по дате
    sort_choice = get_user_choice("\nОтсортировать операции по дате? Да/Нет: ", ["да", "нет", "д", "н"])

    if sort_choice in ["да", "д"]:
        order_choice = get_user_choice(
            "Отсортировать по возрастанию или по убыванию? (возрастание/убывание): ",
            ["возрастание", "убывание", "в", "у"],
        )

        reverse = order_choice in ["убывание", "у"]
        filtered_transactions = sort_transactions(filtered_transactions, reverse)
        order_text = "убыванию" if reverse else "возрастанию"
        print(f"Операции отсортированы по дате по {order_text}")

    # Фильтрация рублевых транзакций
    rub_choice = get_user_choice("\nВыводить только рублевые транзакции? Да/Нет: ", ["да", "нет", "д", "н"])

    if rub_choice in ["да", "д"]:
        filtered_transactions = filter_rub_transactions(filtered_transactions)
        print("Выведены только рублевые транзакции")

    # Поиск по описанию
    search_choice = get_user_choice(
        "\nОтфильтровать список транзакций по определенному слову в описании? Да/Нет: ", ["да", "нет", "д", "н"]
    )

    if search_choice in ["да", "д"]:
        search_word = input("Введите слово для поиска в описании: ").strip()
        if search_word:
            filtered_transactions = process_bank_search(filtered_transactions, search_word)
            print(f'Применен поиск по слову: "{search_word}"')

    # Дополнительная функциональность: подсчет операций по категориям
    count_choice = get_user_choice("\nПоказать статистику по категориям операций? Да/Нет: ", ["да", "нет", "д", "н"])

    if count_choice in ["да", "д"]:
        # Автоматически определяем категории из описаний
        categories = set()
        for transaction in filtered_transactions:
            description = transaction.get("description", "")
            if description:
                # Берем первое слово как категорию
                first_word = description.split()[0] if description.split() else ""
                if first_word:
                    categories.add(first_word)

        if categories:
            categories_list = list(categories)
            operations_count = process_bank_operations(filtered_transactions, categories_list)
            print("\nСтатистика операций по категориям:")
            for category, count in operations_count.items():
                print(f"  {category}: {count} операций")
        else:
            print("Не удалось определить категории операций.")

    # Вывод результата
    print("\nРаспечатываю итоговый список транзакций...\n")
    display_transactions(filtered_transactions)


if __name__ == "__main__":
    main()
