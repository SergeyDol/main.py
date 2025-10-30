import pytest

from src.utils.transaction_operations import process_bank_operations, process_bank_search


class TestTransactionOperations:
    """Тесты для операций с транзакциями."""

    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми транзакциями."""
        return [
            {
                "id": 1,
                "date": "2023-01-01",
                "description": "Перевод организации",
                "status": "EXECUTED",
                "amount": "1000",
                "currency": "RUB",
            },
            {
                "id": 2,
                "date": "2023-01-02",
                "description": "Открытие вклада",
                "status": "EXECUTED",
                "amount": "500",
                "currency": "USD",
            },
            {
                "id": 3,
                "date": "2023-01-03",
                "description": "Перевод с карты на карту",
                "status": "CANCELED",
                "amount": "200",
                "currency": "RUB",
            },
            {
                "id": 4,
                "date": "2023-01-04",
                "description": "Оплата услуг",
                "status": "PENDING",
                "amount": "1500",
                "currency": "EUR",
            },
        ]

    def test_process_bank_search_found(self, sample_transactions):
        """Тест поиска транзакций - найденные результаты."""
        result = process_bank_search(sample_transactions, "перевод")
        assert len(result) == 2
        assert all("перевод" in transaction["description"].lower() for transaction in result)

    def test_process_bank_search_not_found(self, sample_transactions):
        """Тест поиска транзакций - результаты не найдены."""
        result = process_bank_search(sample_transactions, "несуществующееслово")
        assert len(result) == 0

    def test_process_bank_search_case_insensitive(self, sample_transactions):
        """Тест поиска транзакций без учета регистра."""
        result = process_bank_search(sample_transactions, "ПЕРЕВОД")
        assert len(result) == 2

    def test_process_bank_search_empty_data(self):
        """Тест поиска с пустыми данными."""
        result = process_bank_search([], "перевод")
        assert len(result) == 0

        result = process_bank_search([{"description": "test"}], "")
        assert len(result) == 0

    def test_process_bank_operations_success(self, sample_transactions):
        """Тест подсчета операций по категориям."""
        categories = ["перевод", "вклад"]
        result = process_bank_operations(sample_transactions, categories)

        assert "перевод" in result
        assert "вклад" in result
        assert result["перевод"] == 2
        assert result["вклад"] == 1

    def test_process_bank_operations_case_insensitive(self, sample_transactions):
        """Тест подсчета операций без учета регистра."""
        categories = ["ПЕРЕВОД", "ВКЛАД"]
        result = process_bank_operations(sample_transactions, categories)

        assert "ПЕРЕВОД" in result
        assert "ВКЛАД" in result
        assert result["ПЕРЕВОД"] == 2
        assert result["ВКЛАД"] == 1

    def test_process_bank_operations_empty_categories(self, sample_transactions):
        """Тест подсчета операций с пустыми категориями."""
        result = process_bank_operations(sample_transactions, [])
        assert result == {}

    def test_process_bank_operations_empty_data(self):
        """Тест подсчета операций с пустыми данными."""
        result = process_bank_operations([], ["перевод"])
        assert result == {}

    def test_process_bank_operations_no_matches(self, sample_transactions):
        """Тест подсчета операций без совпадений."""
        categories = ["несуществующаякатегория"]
        result = process_bank_operations(sample_transactions, categories)

        assert "несуществующаякатегория" in result
        assert result["несуществующаякатегория"] == 0
