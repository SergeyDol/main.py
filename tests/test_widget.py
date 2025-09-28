import pytest

from src.widget import get_date, mask_account_card


class TestWidget:
    """Тесты для модуля widget.py"""

    @pytest.mark.parametrize(
        "account_info, expected",
        [
            # Карты с указанием типа
            ("Visa Platinum 1234567890123456", "Visa Platinum 1234 56** **** 3456"),
            ("MasterCard 1111222233334444", "MasterCard 1111 22** **** 4444"),
            ("МИР 9999888877776666", "МИР 9999 88** **** 6666"),
            # Счета
            ("Счет 12345678901234567890", "Счет **7890"),
            ("счет 12345678", "счет **5678"),
            ("Account 1234567890", "Account **7890"),  # английский вариант
            # Крайние случаи
            ("1234567890123456", "1234 56** **** 3456"),  # теперь правильно определяется как карта
            ("12345678", "**5678"),  # только номер - обрабатывается как счет
            ("", ""),  # пустая строка
        ]
    )
    def test_mask_account_card_valid(self, account_info, expected):
        """Тестирование корректных входных данных"""
        assert mask_account_card(account_info) == expected

    @pytest.mark.parametrize(
        "account_info, expected",
        [
            ("Visa Platinum 12345", "Visa Platinum 12345"),  # некорректная длина карты
            ("Счет 123", "Счет 123"),  # некорректная длина счета
            ("Just text", "Just text"),  # текст без номера
        ]
    )
    def test_mask_account_card_edge_cases(self, account_info, expected):
        """Тестирование пограничных случаев"""
        assert mask_account_card(account_info) == expected

    @pytest.mark.parametrize(
        "date_string, expected",
        [
            ("2023-10-05T12:30:45.123456", "05.10.2023"),
            ("2020-01-01T00:00:00.000000", "01.01.2020"),
            ("1999-12-31T23:59:59.999999", "31.12.1999"),
            ("2023-10-05T12:30:45.123456Z", "05.10.2023"),  # с Z в конце
        ]
    )
    def test_get_date_valid(self, date_string, expected):
        """Тестирование корректных дат"""
        assert get_date(date_string) == expected

    @pytest.mark.parametrize(
        "invalid_date_string, expected",
        [
            ("invalid-date", "invalid-date"),  # некорректный формат
            ("2023-13-01T12:30:45.123456", "2023-13-01T12:30:45.123456"),  # несуществующий месяц
            ("2023-10-32T12:30:45.123456", "2023-10-32T12:30:45.123456"),  # несуществующий день
            ("", ""),  # пустая строка
            (None, ""),  # None
        ]
    )
    def test_get_date_invalid(self, invalid_date_string, expected):
        """Тестирование некорректных дат - возвращает как есть"""
        result = get_date(invalid_date_string)
        assert result == expected
