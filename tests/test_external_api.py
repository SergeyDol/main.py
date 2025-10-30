import os
from unittest.mock import Mock, patch

import pytest

from src.external_api import convert_amount_to_rub, get_exchange_rate


class TestExternalAPI:
    """Тесты для модуля external_api"""

    @patch("src.external_api.requests.get")
    def test_get_exchange_rate_success(self, mock_get):
        """Тестирование успешного получения курса валют"""
        # Мокаем ответ API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": {"RUB": 92.5}}
        mock_get.return_value = mock_response

        # Мокаем переменную окружения
        with patch.dict(os.environ, {"EXCHANGE_RATE_API_KEY": "test_key"}):
            rate = get_exchange_rate("USD", "RUB")

        assert rate == 92.5
        mock_get.assert_called_once()

    @patch("src.external_api.requests.get")
    def test_get_exchange_rate_failure(self, mock_get):
        """Тестирование неудачного получения курса валют"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {"EXCHANGE_RATE_API_KEY": "test_key"}):
            rate = get_exchange_rate("USD", "RUB")

        assert rate is None

    @patch("src.external_api.requests.get")
    def test_get_exchange_rate_no_api_key(self, mock_get):
        """Тестирование отсутствия API ключа"""
        # Удаляем переменную окружения если существует
        if "EXCHANGE_RATE_API_KEY" in os.environ:
            del os.environ["EXCHANGE_RATE_API_KEY"]

        with pytest.raises(ValueError, match="API key not found"):
            get_exchange_rate("USD", "RUB")

    @patch("src.external_api.get_exchange_rate")
    def test_convert_amount_to_rub_rub(self, mock_rate):
        """Тестирование конвертации RUB в RUB"""
        transaction = {"operationAmount": {"amount": "100.50", "currency": {"code": "RUB"}}}

        result = convert_amount_to_rub(transaction)
        assert result == 100.50
        mock_rate.assert_not_called()

    @patch("src.external_api.get_exchange_rate")
    def test_convert_amount_to_rub_usd(self, mock_rate):
        """Тестирование конвертации USD в RUB"""
        mock_rate.return_value = 92.5

        transaction = {"operationAmount": {"amount": "100.0", "currency": {"code": "USD"}}}

        result = convert_amount_to_rub(transaction)
        assert result == 9250.0  # 100 * 92.5
        mock_rate.assert_called_once_with("USD", "RUB")

    @patch("src.external_api.get_exchange_rate")
    def test_convert_amount_to_rub_eur(self, mock_rate):
        """Тестирование конвертации EUR в RUB"""
        mock_rate.return_value = 100.0

        transaction = {"operationAmount": {"amount": "50.0", "currency": {"code": "EUR"}}}

        result = convert_amount_to_rub(transaction)
        assert result == 5000.0  # 50 * 100.0
        mock_rate.assert_called_once_with("EUR", "RUB")

    @patch("src.external_api.get_exchange_rate")
    def test_convert_amount_to_rub_rate_error(self, mock_rate):
        """Тестирование ошибки при получении курса валют"""
        mock_rate.return_value = None

        transaction = {"operationAmount": {"amount": "100.0", "currency": {"code": "USD"}}}

        with pytest.raises(ValueError, match="Could not get exchange rate for USD"):
            convert_amount_to_rub(transaction)

    def test_convert_amount_to_rub_invalid_amount(self):
        """Тестирование конвертации с некорректной суммой"""
        transaction = {"operationAmount": {"amount": "invalid", "currency": {"code": "RUB"}}}

        result = convert_amount_to_rub(transaction)
        assert result == 0.0

    def test_convert_amount_to_rub_missing_data(self):
        """Тестирование конвертации с отсутствующими данными"""
        # Транзакция без operationAmount
        transaction = {"id": 1}
        result = convert_amount_to_rub(transaction)
        assert result == 0.0

        # Транзакция без amount
        transaction = {"operationAmount": {"currency": {"code": "RUB"}}}
        result = convert_amount_to_rub(transaction)
        assert result == 0.0
