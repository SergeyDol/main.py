import pytest

from src.widget import get_date, mask_account_card


class TestWidget:
    """Тесты для модуля widget"""

    # Тесты для mask_account_card
    @pytest.mark.parametrize(
        "input_str, expected",
        [
            ("Счет 12345678901234567890", "Счет **7890"),
            ("Visa Platinum 1234567812345678", "Visa Platinum 1234 56** **** 5678"),
            ("MasterCard 5555666677778888", "MasterCard 5555 66** **** 8888"),
            ("Maestro 1234123412341234", "Maestro 1234 12** **** 1234"),
            ("Счет 09876543210987654321", "Счет **4321"),
        ],
    )
    def test_mask_account_card_valid(self, input_str: str, expected: str) -> None:
        """Тестирование корректного определения типа и маскирования"""
        assert mask_account_card(input_str) == expected

    def test_mask_account_card_no_number(self) -> None:
        """Тестирование обработки строки без номера"""
        assert mask_account_card("Счет") == "Счет"
        assert mask_account_card("Visa Platinum") == "Visa Platinum"

    def test_mask_account_card_empty(self) -> None:
        """Тестирование обработки пустой строки"""
        assert mask_account_card("") == ""

    def test_mask_account_card_none(self) -> None:
        """Тестирование обработки None"""
        # Тестируем, что функция корректно обрабатывает None
        result = mask_account_card(None)  # type: ignore
        assert result is None or result == ""

    def test_mask_account_card_unknown_type(self) -> None:
        """Тестирование обработки неизвестного типа"""
        assert mask_account_card("Unknown 1234567812345678") == "Unknown 1234 56** **** 5678"

    # Тесты для get_date
    @pytest.mark.parametrize(
        "input_date, expected",
        [
            ("2023-10-01T12:00:00.000000", "01.10.2023"),
            ("2023-09-15T08:30:00.000000", "15.09.2023"),
            ("2023-11-05T16:45:00.000000", "05.11.2023"),
            ("2023-08-20T10:15:00.000000", "20.08.2023"),
        ],
    )
    def test_get_date_valid(self, input_date: str, expected: str) -> None:
        """Тестирование корректного преобразования даты"""
        assert get_date(input_date) == expected

    def test_get_date_invalid_format(self) -> None:
        """Тестирование обработки неверного формата даты"""
        with pytest.raises(ValueError):
            get_date("2023-10-01")

    def test_get_date_empty(self) -> None:
        """Тестирование обработки пустой строки"""
        with pytest.raises(ValueError):
            get_date("")

    def test_get_date_none(self) -> None:
        """Тестирование обработки None"""
        # Тестируем, что функция корректно обрабатывает None
        result = get_date(None)  # type: ignore
        assert result is None or result == ""

    def test_get_date_malformed(self) -> None:
        """Тестирование обработки поврежденной даты"""
        with pytest.raises(ValueError):
            get_date("2023-13-01T12:00:00.000000")
