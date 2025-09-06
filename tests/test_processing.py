import pytest
from datetime import datetime
from src.processing import filter_by_state, sort_by_date


class TestProcessing:
    """Тесты для модуля processing.py"""

    @pytest.fixture
    def sample_operations(self):
        return [
            {"id": 1, "state": "EXECUTED", "date": "2023-10-05T12:30:45.123456"},
            {"id": 2, "state": "PENDING", "date": "2023-10-04T10:15:30.987654"},
            {"id": 3, "state": "EXECUTED", "date": "2023-10-03T08:45:12.654321"},
            {"id": 4, "state": "CANCELED", "date": "2023-10-02T16:20:18.321987"},
            {"id": 5, "state": "EXECUTED", "date": "2023-10-01T14:10:05.789123"},
            {"id": 6, "state": "EXECUTED"},  # без даты
            {"id": 7, "date": "2023-09-30T09:05:25.456789"},  # без state
        ]

    def test_filter_by_state_executed(self, sample_operations):
        """Тестирование фильтрации по EXECUTED"""
        result = filter_by_state(sample_operations, "EXECUTED")
        # Должно быть 4 операции с state="EXECUTED" (id: 1, 3, 5, 6)
        assert len(result) == 4
        assert all(op["state"] == "EXECUTED" for op in result)

    def test_filter_by_state_pending(self, sample_operations):
        """Тестирование фильтрации по PENDING"""
        result = filter_by_state(sample_operations, "PENDING")
        assert len(result) == 1
        assert result[0]["state"] == "PENDING"

    def test_sort_by_date_descending(self, sample_operations):
        """Тестирование сортировки по убыванию даты"""
        result = sort_by_date(sample_operations, reverse=True)

        # Получаем только операции с датами
        operations_with_dates = [op for op in result if "date" in op]
        dates = [op["date"] for op in operations_with_dates]

        # Проверяем сортировку
        parsed_dates = []
        for date_str in dates:
            try:
                parsed_dates.append(datetime.fromisoformat(date_str.replace("Z", "+00:00")))
            except (ValueError, TypeError):
                pass

        if len(parsed_dates) > 1:
            for i in range(len(parsed_dates) - 1):
                assert parsed_dates[i] >= parsed_dates[i + 1]
