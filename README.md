# Банковский проект - Обработка транзакций

Проект предоставляет инструменты для работы с банковскими транзакциями, включая маскировку данных, фильтрацию, сортировку и генерацию данных.

## Установка

1. Клонируйте репозиторий
2. Установите зависимости: `pip install -r requirements.txt`
3. Установите проект: `pip install -e .`

## Модули

### masks.py
Функции для маскировки банковских карт и счетов:

- `get_mask_card_number(card_number: str) -> str` - маскирует номер карты
- `get_mask_account(account_number: str) -> str` - маскирует номер счета

### processing.py
Функции для обработки списков транзакций:

- `filter_by_state(operations: List[Dict], state: str = "EXECUTED") -> List[Dict]` - фильтрация по статусу
- `sort_by_date(operations: List[Dict], reverse: bool = True) -> List[Dict]` - сортировка по дате

### widget.py
Утилиты для работы с банковскими данными:

- `mask_account_card(account_info: str) -> str` - маскирует карту/счет в строке
- `get_date(date_string: str) -> str` - преобразует формат даты

### generators.py (НОВЫЙ)
Генераторы для эффективной работы с большими объемами данных:

#### `filter_by_currency(transactions: List[Dict], currency_code: str) -> Iterator[Dict]`
Фильтрует транзакции по заданной валюте и возвращает итератор.

**Пример:**
```python
from src.generators import filter_by_currency

usd_transactions = filter_by_currency(transactions, "USD")
for transaction in usd_transactions:
    print(transaction["id"], transaction["operationAmount"]["amount"])
transaction_descriptions(transactions: List[Dict]) -> Iterator[str]
Возвращает итератор с описаниями всех транзакций.
