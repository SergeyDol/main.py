#Проект по обработке банковских операций
##Цель проекта:
Проект предоставляет набор утилит для обработки и анализа банковских операций. Основные функции включают фильтрацию операций по статусу, сортировку по дате, маскировку номеров карт и счетов, а также форматирование дат.
## Установка:

1. Клонируйте репозиторий:
```
git@github.com:SergeyDol/main.py.git
```
2. Установите зависимости:
```
pip install -r requirements.txt
```
## Использование:
Загрузить файл, запустить

##Использование
###Импорт модулей
python
```
from src.masks import get_mask_card_number, get_mask_account
from src.processing import filter_by_state, sort_by_date
from src.utils import load_operations, display_operations
```
