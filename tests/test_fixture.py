from datetime import datetime

import pytest


@pytest.fixture
def sample_card_numbers():
    """Общая фикстура для номеров карт"""
    return {
        "valid": "1234567890123456",
        "invalid_short": "123456789012345",
        "invalid_long": "12345678901234567",
        "invalid_chars": "1234567890abcdef",
    }


@pytest.fixture
def sample_account_numbers():
    """Общая фикстура для номеров счетов"""
    return {
        "valid_long": "12345678901234567890",
        "valid_short": "1234",
        "invalid_short": "123",
        "invalid_chars": "abcd",
    }
