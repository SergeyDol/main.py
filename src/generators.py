from typing import Any, Dict, Iterator, List


def filter_by_currency(transactions: List[Dict[str, Any]], currency_code: str) -> Iterator[Dict[str, Any]]:
    """
    Фильтрует транзакции по заданной валюте.

    Args:
        transactions: Список словарей с транзакциями
        currency_code: Код валюты для фильтрации (например, "USD", "RUB")

    Yields:
        Словари транзакций, где валюта операции соответствует заданной
    """
    for transaction in transactions:
        operation_amount = transaction.get("operationAmount", {})
        currency = operation_amount.get("currency", {})
        if currency.get("code") == currency_code:
            yield transaction


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Iterator[str]:
    """
    Генерирует описания операций из списка транзакций.

    Args:
        transactions: Список словарей с транзакциями

    Yields:
        Описания операций по очереди
    """
    for transaction in transactions:
        yield transaction.get("description", "")


def card_number_generator(start: int, end: int) -> Iterator[str]:
    """
    Генерирует номера банковских карт в заданном диапазоне.

    Args:
        start: Начальный номер карты (включительно)
        end: Конечный номер карты (включительно)

    Yields:
        Номера карт в формате "XXXX XXXX XXXX XXXX"

    Raises:
        ValueError: Если start > end или значения выходят за допустимые пределы
    """
    # Проверка входных данных
    if start < 1:
        raise ValueError("Start value must be at least 1")
    if start > end:
        raise ValueError("Start value cannot be greater than end value")
    if end > 9999999999999999:
        raise ValueError("End value exceeds maximum card number (9999999999999999)")

    for number in range(start, end + 1):
        # Форматируем номер в 16-значный строковый формат с ведущими нулями
        card_number = str(number).zfill(16)
        # Разбиваем на группы по 4 цифры
        formatted_number = f"{card_number[:4]} {card_number[4:8]} {card_number[8:12]} {card_number[12:16]}"
        yield formatted_number
