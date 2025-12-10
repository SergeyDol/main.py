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

    target_state = state.upper().strip()

    filtered_operations = []
    for operation in operations:
        # Ищем поле state в разных вариантах написания
        operation_state = None

        # Пробуем разные варианты ключей
        possible_keys = ['state', 'State', 'STATE', 'status', 'Status', 'STATUS']

        for key in possible_keys:
            if key in operation and operation[key]:
                operation_state = str(operation[key]).upper().strip()
                break

        # Если нашли state и он совпадает с целевым
        if operation_state and operation_state == target_state:
            filtered_operations.append(operation)

    return filtered_operations


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