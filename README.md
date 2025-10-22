# Банковский проект - Обработка транзакций

Проект предоставляет инструменты для работы с банковскими транзакциями, включая маскировку данных, фильтрацию, сортировку и генерацию данных.

## Установка

1. Клонируйте репозиторий
2. Установите зависимости: `pip install -r requirements.txt`
3. Установите проект: `pip install -e .`

## Модули
## Модуль utils.py
Функции для работы с файлами:

#### `read_json_file(file_path: str) -> List[Dict]`
Читает JSON-файл и возвращает список транзакций.

```python
from src.utils import read_json_file

transactions = read_json_file("data/operations.json")

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

Пример:

python
from src.generators import transaction_descriptions

descriptions = transaction_descriptions(transactions)
for description in descriptions:
    print(description)
card_number_generator(start: int, end: int) -> Iterator[str]
Генерирует номера банковских карт в заданном диапазоне.

Пример:

python
from src.generators import card_number_generator

# Генерация первых 5 номеров карт
for card_number in card_number_generator(1, 5):
    print(card_number)

# Output:
# 0000 0000 0000 0001
# 0000 0000 0000 0002
# 0000 0000 0000 0003
# 0000 0000 0000 0004
# 0000 0000 0000 0005
Тестирование
Для запуска тестов:

bash
pytest --cov=src --cov-report=html
Отчет о покрытии тестами будет доступен в папке htmlcov/index.html

Примеры использования
python
from src import masks, processing, widget, generators

# Маскировка данных
masked_card = masks.get_mask_card_number("1234567890123456")
masked_account = masks.get_mask_account("12345678901234567890")

# Обработка транзакций
executed_operations = processing.filter_by_state(transactions, "EXECUTED")
sorted_operations = processing.sort_by_date(transactions)

# Работа с датами
formatted_date = widget.get_date("2023-10-05T12:30:45.123456")

# Использование генераторов
usd_transactions = generators.filter_by_currency(transactions, "USD")
descriptions = generators.transaction_descriptions(transactions)
card_numbers = generators.card_number_generator(1, 100)
Требования
Python 3.7+

pytest для тестирования

flake8 для проверки стиля кода

Структура проекта
text
src/
├── __init__.py
├── masks.py          # Маскировка карт и счетов
├── processing.py     # Фильтрация и сортировка
├── widget.py         # Утилиты
└── generators.py     # Генераторы (НОВЫЙ)
tests/
├── test_masks.py
├── test_processing.py
├── test_widget.py
└── test_generators.py # Тесты для генераторов

## decorators.py (НОВЫЙ)
Декораторы для расширения функциональности функций:

#### `log(filename: Optional[str] = None) -> Callable`
Декоратор для логирования выполнения функций.

**Параметры:**
- `filename`: Имя файла для записи логов. Если None, логи выводятся в консоль.

**Примеры:**
```python
from src.decorators import log

# Логирование в консоль
@log()
def add(a, b):
    return a + b

add(1, 2)  # Вывод в консоль: 2023-10-05 12:30:45 - add ok

# Логирование в файл
@log(filename="operations.log")
def multiply(x, y):
    return x * y

multiply(3, 4)  # Запись в файл: 2023-10-05 12:30:45 - multiply ok

# Логирование ошибок.
@log()
def divide(a, b):
    return a / b

divide(1, 0)  # Вывод в консоль: 2023-10-05 12:30:45 - divide error: ZeroDivisionError. Inputs: (1, 0), {}
## 📁 Модуль file_reader.py

Функции для чтения финансовых операций из различных форматов файлов.

### `read_csv_file(file_path: str) -> List[Dict]`
Читает CSV-файл и возвращает список транзакций.

### `read_excel_file(file_path: str, sheet_name: str = 0) -> List[Dict]`  
Читает Excel-файл и возвращает список транзакций.

### `detect_file_type_and_read(file_path: str) -> List[Dict]`
Автоматически определяет тип файла и читает данные соответствующим способом.

**Примеры использования:**
```python
from src.file_reader import read_csv_file, read_excel_file

# Чтение CSV файла
csv_transactions = read_csv_file("data/transactions.csv")

# Чтение Excel файла  
excel_transactions = read_excel_file("data/transactions_excel.xlsx")

# Автоматическое определение типа
transactions = detect_file_type_and_read("data/operations.json")