import pytest
from src.masks import get_mask_card_number, get_mask_account


class TestMasks:
    """Тесты для модуля masks.py"""

    # Тесты для get_mask_card_number
    @pytest.mark.parametrize(
        "card_number, expected",
        [
            ("1234567890123456", "1234 56** **** 3456"),
            ("1111222233334444", "1111 22** **** 4444"),
            ("9999888877776666", "9999 88** **** 6666"),
        ]
    )
    def test_get_mask_card_number_valid(self, card_number, expected):
        """Тестирование корректных номеров карт"""
        assert get_mask_card_number(card_number) == expected

    @pytest.mark.parametrize(
        "invalid_card_number",
        [
            "123456789012345",  # 15 цифр
            "12345678901234567",  # 17 цифр
            "1234567890abcdef",  # не цифры
            "",  # пустая строка
            None,  # None
            1234567890123456,  # число вместо строки
        ]
    )
    def test_get_mask_card_number_invalid(self, invalid_card_number):
        """Тестирование некорректных номеров карт"""
        with pytest.raises(ValueError, match="Номер карты должен быть строкой из 16 цифр"):
            get_mask_card_number(invalid_card_number)

    # Тесты для get_mask_account
    @pytest.mark.parametrize(
        "account_number, expected",
        [
            ("12345678", "**5678"),
            ("1234", "**1234"),
            ("1234567890123456", "**3456"),
        ]
    )
    def test_get_mask_account_valid(self, account_number, expected):
        """Тестирование корректных номеров счетов"""
        assert get_mask_account(account_number) == expected

    @pytest.mark.parametrize(
        "invalid_account_number",
        [
            "123",  # 3 цифры
            "abc",  # не цифры
            "",  # пустая строка
            None,  # None
            1234,  # число вместо строки
        ]
    )
    def test_get_mask_account_invalid(self, invalid_account_number):
        """Тестирование некорректных номеров счетов"""
        with pytest.raises(ValueError, match="Номер счёта должен быть строкой с минимум 4 цифрами"):
            get_mask_account(invalid_account_number)
