import pytest

from src.masks import get_mask_account, get_mask_card_number


class TestMasks:
    """Тесты для модуля masks"""

    # Тесты для get_mask_card_number
    @pytest.mark.parametrize(
        "input_card, expected",
        [
            ("1234567812345678", "1234 56** **** 5678"),
            ("5555666677778888", "5555 66** **** 8888"),
            ("1111222233334444", "1111 22** **** 4444"),
            ("9999888877776666", "9999 88** **** 6666"),
        ],
    )
    def test_get_mask_card_number_valid(self, input_card: str, expected: str) -> None:
        """Тестирование корректного маскирования номеров карт"""
        assert get_mask_card_number(input_card) == expected

    def test_get_mask_card_number_short(self) -> None:
        """Тестирование обработки короткого номера карты"""
        with pytest.raises(ValueError):
            get_mask_card_number("12345678")

    def test_get_mask_card_number_empty(self) -> None:
        """Тестирование обработки пустой строки"""
        with pytest.raises(ValueError):
            get_mask_card_number("")

    def test_get_mask_card_number_none(self) -> None:
        """Тестирование обработки None"""
        # Тестируем, что функция корректно обрабатывает None
        result = get_mask_card_number(None)  # type: ignore
        assert result is None or result == ""

    def test_get_mask_card_number_non_digits(self) -> None:
        """Тестирование обработки нечисловых символов"""
        with pytest.raises(ValueError):
            get_mask_card_number("abcd1234efgh5678")

    # Тесты для get_mask_account
    @pytest.mark.parametrize(
        "input_account, expected",
        [
            ("12345678901234567890", "**7890"),
            ("09876543210987654321", "**4321"),
            ("11112222333344445555", "**5555"),
            ("44443333222211110000", "**0000"),
        ],
    )
    def test_get_mask_account_valid(self, input_account: str, expected: str) -> None:
        """Тестирование корректного маскирования номеров счетов"""
        assert get_mask_account(input_account) == expected

    def test_get_mask_account_short(self) -> None:
        """Тестирование обработки короткого номера счета"""
        with pytest.raises(ValueError):
            get_mask_account("123456")

    def test_get_mask_account_empty(self) -> None:
        """Тестирование обработки пустой строки"""
        with pytest.raises(ValueError):
            get_mask_account("")

    def test_get_mask_account_none(self) -> None:
        """Тестирование обработки None"""
        # Тестируем, что функция корректно обрабатывает None
        result = get_mask_account(None)  # type: ignore
        assert result is None or result == ""

    def test_get_mask_account_non_digits(self) -> None:
        """Тестирование обработки нечисловых символов"""
        with pytest.raises(ValueError):
            get_mask_account("abcdefghijklmnopqrst")
