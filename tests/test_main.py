import pytest
from unittest.mock import patch, MagicMock
from src.main import filter_by_status, sort_transactions, filter_rub_transactions, format_transaction


class TestMain:
    """Тесты для модуля main"""

    def test_filter_by_status(self):
        """Тестирование фильтрации по статусу"""
        transactions = [
            {"id": 1, "state": "EXECUTED", "amount": "100"},
            {"id": 2, "state": "CANCELED", "amount": "200"},
            {"id": 3, "state": "EXECUTED", "amount": "300"},
        ]

        result = filter_by_status(transactions, "EXECUTED")
        assert len(result) == 2
        assert all(t["state"].lower() == "executed" for t in result)

    def test_filter_by_status_case_insensitive(self):
        """Тестирование фильтрации по статусу без учета регистра"""
        transactions = [
            {"id": 1, "state": "executed", "amount": "100"},
            {"id": 2, "state": "EXECUTED", "amount": "200"},
        ]

        result = filter_by_status(transactions, "EXECUTED")
        assert len(result) == 2

    def test_sort_transactions_ascending(self):
        """Тестирование сортировки по возрастанию"""
        transactions = [
            {"id": 1, "date": "2023-01-02"},
            {"id": 2, "date": "2023-01-01"},
            {"id": 3, "date": "2023-01-03"},
        ]

        result = sort_transactions(transactions, reverse=False)
        assert result[0]["id"] == 2
        assert result[1]["id"] == 1
        assert result[2]["id"] == 3

    def test_sort_transactions_descending(self):
        """Тестирование сортировки по убыванию"""
        transactions = [
            {"id": 1, "date": "2023-01-01"},
            {"id": 2, "date": "2023-01-02"},
            {"id": 3, "date": "2023-01-03"},
        ]

        result = sort_transactions(transactions, reverse=True)
        assert result[0]["id"] == 3
        assert result[1]["id"] == 2
        assert result[2]["id"] == 1

    def test_filter_rub_transactions(self):
        """Тестирование фильтрации рублевых транзакций"""
        transactions = [
            {"id": 1, "operationAmount": {"amount": "100", "currency": {"code": "RUB"}}},
            {"id": 2, "operationAmount": {"amount": "200", "currency": {"code": "USD"}}},
            {"id": 3, "operationAmount": {"amount": "300", "currency": {"code": "RUB"}}},
        ]

        result = filter_rub_transactions(transactions)
        assert len(result) == 2
        assert all(t["operationAmount"]["currency"]["code"] == "RUB" for t in result)

    def test_format_transaction_card_to_card(self):
        """Тестирование форматирования транзакции карта-карта"""
        transaction = {
            "date": "2023-01-01T10:00:00",
            "description": "Перевод с карты на карту",
            "from": "Visa Platinum 1234567890123456",
            "to": "MasterCard 9876543210987654",
            "operationAmount": {
                "amount": "100.50",
                "currency": {"code": "RUB", "name": "руб."}
            }
        }

        result = format_transaction(transaction)
        assert "2023-01-01" in result
        assert "Перевод с карты на карту" in result
        assert "Visa Platinum 1234 56** **** 3456" in result
        assert "MasterCard 9876 54** **** 7654" in result
        assert "100.50" in result

    def test_format_transaction_account(self):
        """Тестирование форматирования транзакции со счетом"""
        transaction = {
            "date": "2023-01-01T10:00:00",
            "description": "Перевод организации",
            "to": "Счет 12345678901234567890",
            "operationAmount": {
                "amount": "500.75",
                "currency": {"code": "RUB", "name": "руб."}
            }
        }

        result = format_transaction(transaction)
        assert "Счет **7890" in result

    @patch('src.main.convert_amount_to_rub')
    def test_format_transaction_with_conversion(self, mock_convert):
        """Тестирование форматирования с конвертацией в рубли"""
        mock_convert.return_value = 7500.0

        transaction = {
            "date": "2023-01-01T10:00:00",
            "description": "Перевод",
            "operationAmount": {
                "amount": "100",
                "currency": {"code": "USD", "name": "USD"}
            }
        }

        result = format_transaction(transaction)
        assert "7500.00 руб." in result


class TestMainIntegration:
    """Интеграционные тесты для main"""

    @patch('src.main.detect_file_type_and_read')
    @patch('src.main.input')
    def test_main_flow_json(self, mock_input, mock_detect):
        """Тестирование основного потока для JSON"""
        # Мокаем ввод пользователя
        mock_input.side_effect = [
            "1",  # Выбор JSON
            "test.json",  # Путь к файлу
            "EXECUTED",  # Статус
            "нет",  # Сортировка
            "нет",  # Рублевые
            "нет"  # Поиск по описанию
        ]

        # Мокаем чтение файла
        mock_detect.return_value = [
            {
                "id": 1,
                "state": "EXECUTED",
                "date": "2023-01-01T10:00:00",
                "description": "Перевод",
                "operationAmount": {
                    "amount": "100",
                    "currency": {"code": "RUB", "name": "руб."}
                }
            }
        ]

        # Запускаем main (должен работать без ошибок)
        from src.main import main
        main()