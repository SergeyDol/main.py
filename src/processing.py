from datetime import datetime
from typing import Any, Dict, List


def filter_by_state(operations: List[Dict[str, Any]], state: str = "EXECUTED") -> List[Dict[str, Any]]:
    """
    Фильтрует список операций по состоянию.

    Args:
        operations: Список операций
        state: Статус для фильтрации (по умолчанию EXECUTED)

    Returns:
        Отфильтрованный список операций
    """
    if not operations:
        return []

    return [operation for operation in operations if operation.get("state") == state]


def sort_by_date(operations: List[Dict[str, Any]], reverse: bool = True) -> List[Dict[str, Any]]:
    """
    Сортирует список операций по дате.

    Args:
        operations: Список операций
        reverse: Если True - по убыванию, False - по возрастанию

    Returns:
        Отсортированный список операций
    """
    if not operations:
        return []

    def get_date_key(operation: Dict[str, Any]) -> datetime:
        """Вспомогательная функция для получения даты из операции."""
        date_str = operation.get("date")
        if date_str:
            try:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                return datetime.min
        return datetime.min

    return sorted(operations, key=get_date_key, reverse=reverse)