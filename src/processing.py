from datetime import datetime
from typing import Any, Dict, List


def filter_by_state(operations: List[Dict[str, Any]], state: str = "EXECUTED") -> List[Dict[str, Any]]:
    """Фильтрует список операций по состоянию."""
    if not operations:
        return []

    return [operation for operation in operations if operation.get("state") == state]


def get_date_key(operation: Dict[str, Any]) -> datetime:
    """Вспомогательная функция для получения даты из операции."""
    date_str = operation.get("date")
    if date_str:
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            # Если дата некорректна, возвращаем минимальную дату
            return datetime.min
    return datetime.min


def sort_by_date(operations: List[Dict[str, Any]], reverse: bool = True) -> List[Dict[str, Any]]:
    """Сортирует список операций по дате."""
    if not operations:
        return []

    # Сортируем операции по дате
    sorted_operations = sorted(operations, key=get_date_key, reverse=reverse)
    return sorted_operations
