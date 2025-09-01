import pytest


class TestProcessing:
    """Тесты для модуля processing"""

    def test_filter_by_state_executed(self, sample_transactions):
        """Тестирование фильтрации по статусу EXECUTED"""
        from src.processing import filter_by_state
        result = filter_by_state(sample_transactions, "EXECUTED")
        assert len(result) == 2
        assert all(item["state"] == "EXECUTED" for item in result)

    def test_filter_by_state_pending(self, sample_transactions):
        """Тестирование фильтрации по статусу PENDING"""
        from src.processing import filter_by_state
        result = filter_by_state(sample_transactions, "PENDING")
        assert len(result) == 1
        assert all(item["state"] == "PENDING" for item in result)

    def test_filter_by_state_canceled(self, sample_transactions):
        """Тестирование фильтрации по статусу CANCELED"""
        from src.processing import filter_by_state
        result = filter_by_state(sample_transactions, "CANCELED")
        assert len(result) == 1
        assert all(item["state"] == "CANCELED" for item in result)

    def test_filter_by_state_nonexistent(self, sample_transactions):
        """Тестирование фильтрации по несуществующему статусу"""
        from src.processing import filter_by_state
        result = filter_by_state(sample_transactions, "NONEXISTENT")
        assert len(result) == 0

    def test_filter_by_state_empty_list(self, sample_empty_transactions):
        """Тестирование фильтрации пустого списка"""
        from src.processing import filter_by_state
        result = filter_by_state(sample_empty_transactions, "EXECUTED")
        assert len(result) == 0

    def test_filter_by_state_invalid_state(self, sample_transactions):
        """Тестирование с неверным типом статуса"""
        from src.processing import filter_by_state
        with pytest.raises(TypeError):
            filter_by_state(sample_transactions, 123)
