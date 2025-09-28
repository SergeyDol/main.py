import pytest

from src.generators import card_number_generator, filter_by_currency, transaction_descriptions


class TestGenerators:
    """Тесты для модуля generators.py"""

    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми транзакциями"""
        return [
            {
                "id": 939719570,
                "state": "EXECUTED",
                "date": "2018-06-30T02:08:58.425572",
                "operationAmount": {
                    "amount": "9824.07",
                    "currency": {
                        "name": "USD",
                        "code": "USD"
                    }
                },
                "description": "Перевод организации",
                "from": "Счет 75106830613657916952",
                "to": "Счет 11776614605963066702"
            },
            {
                "id": 142264268,
                "state": "EXECUTED",
                "date": "2019-04-04T23:20:05.206878",
                "operationAmount": {
                    "amount": "79114.93",
                    "currency": {
                        "name": "USD",
                        "code": "USD"
                    }
                },
                "description": "Перевод со счета на счет",
                "from": "Счет 19708645243227258542",
                "to": "Счет 75651667383060284188"
            },
            {
                "id": 873106923,
                "state": "EXECUTED",
                "date": "2019-03-23T01:09:46.296404",
                "operationAmount": {
                    "amount": "43318.34",
                    "currency": {
                        "name": "руб.",
                        "code": "RUB"
                    }
                },
                "description": "Перевод со счета на счет",
                "from": "Счет 44812258784861134719",
                "to": "Счет 74489636417521191160"
            },
            {
                "id": 895315941,
                "state": "EXECUTED",
                "date": "2018-08-19T04:27:37.904916",
                "operationAmount": {
                    "amount": "56883.54",
                    "currency": {
                        "name": "USD",
                        "code": "USD"
                    }
                },
                "description": "Перевод с карты на карту",
                "from": "Visa Classic 6831982476737658",
                "to": "Visa Platinum 8990922113665229"
            }
        ]

    # Тесты для filter_by_currency
    def test_filter_by_currency_usd(self, sample_transactions):
        """Тестирование фильтрации по USD"""
        usd_transactions = list(filter_by_currency(sample_transactions, "USD"))
        assert len(usd_transactions) == 3
        assert all(
            transaction["operationAmount"]["currency"]["code"] == "USD"
            for transaction in usd_transactions
        )

    def test_filter_by_currency_rub(self, sample_transactions):
        """Тестирование фильтрации по RUB"""
        rub_transactions = list(filter_by_currency(sample_transactions, "RUB"))
        assert len(rub_transactions) == 1
        assert rub_transactions[0]["operationAmount"]["currency"]["code"] == "RUB"

    def test_filter_by_currency_empty(self, sample_transactions):
        """Тестирование фильтрации по несуществующей валюте"""
        eur_transactions = list(filter_by_currency(sample_transactions, "EUR"))
        assert len(eur_transactions) == 0

    def test_filter_by_currency_empty_list(self):
        """Тестирование фильтрации пустого списка"""
        empty_transactions = list(filter_by_currency([], "USD"))
        assert len(empty_transactions) == 0

    def test_filter_by_currency_generator_behavior(self, sample_transactions):
        """Тестирование поведения генератора"""
        generator = filter_by_currency(sample_transactions, "USD")
        # Первый вызов next()
        first_transaction = next(generator)
        assert first_transaction["id"] == 939719570
        # Второй вызов next()
        second_transaction = next(generator)
        assert second_transaction["id"] == 142264268

    # Тесты для transaction_descriptions
    def test_transaction_descriptions(self, sample_transactions):
        """Тестирование генератора описаний транзакций"""
        descriptions = list(transaction_descriptions(sample_transactions))
        expected_descriptions = [
            "Перевод организации",
            "Перевод со счета на счет",
            "Перевод со счета на счет",
            "Перевод с карты на карту"
        ]
        assert descriptions == expected_descriptions

    def test_transaction_descriptions_empty(self):
        """Тестирование генератора описаний для пустого списка"""
        descriptions = list(transaction_descriptions([]))
        assert descriptions == []

    def test_transaction_descriptions_generator_behavior(self, sample_transactions):
        """Тестирование поведения генератора описаний"""
        generator = transaction_descriptions(sample_transactions)
        assert next(generator) == "Перевод организации"
        assert next(generator) == "Перевод со счета на счет"

    # Тесты для card_number_generator
    @pytest.mark.parametrize("start, end, expected", [
        (1, 3, [
            "0000 0000 0000 0001",
            "0000 0000 0000 0002",
            "0000 0000 0000 0003"
        ]),
        (9999999999999995, 9999999999999999, [
            "9999 9999 9999 9995",
            "9999 9999 9999 9996",
            "9999 9999 9999 9997",
            "9999 9999 9999 9998",
            "9999 9999 9999 9999"
        ]),
        (123, 125, [
            "0000 0000 0000 0123",
            "0000 0000 0000 0124",
            "0000 0000 0000 0125"
        ])
    ])
    def test_card_number_generator_range(self, start, end, expected):
        """Тестирование генератора номеров карт в различных диапазонах"""
        result = list(card_number_generator(start, end))
        assert result == expected

    def test_card_number_generator_single(self):
        """Тестирование генератора для одного номера"""
        result = list(card_number_generator(42, 42))
        assert result == ["0000 0000 0000 0042"]

    def test_card_number_generator_format(self):
        """Тестирование формата номеров карт"""
        generator = card_number_generator(1, 1)
        card_number = next(generator)
        # Проверяем формат: 4 группы по 4 цифры, разделенные пробелами
        parts = card_number.split()
        assert len(parts) == 4
        assert all(len(part) == 4 and part.isdigit() for part in parts)

    def test_card_number_generator_invalid_range(self):
        """Тестирование генератора с некорректным диапазоном"""
        with pytest.raises(ValueError, match="Start value cannot be greater than end value"):
            list(card_number_generator(5, 3))  # start > end

    def test_card_number_generator_negative(self):
        """Тестирование генератора с отрицательными значениями"""
        with pytest.raises(ValueError, match="Start value must be at least 1"):
            list(card_number_generator(-1, 5))

    def test_card_number_generator_too_large(self):
        """Тестирование генератора со слишком большими значениями"""
        with pytest.raises(ValueError, match="End value exceeds maximum card number"):
            list(card_number_generator(1, 10000000000000000))  # Превышает 16 цифр