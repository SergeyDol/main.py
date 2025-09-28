import os
import requests
from typing import Dict, Any, Optional


def get_exchange_rate(from_currency: str, to_currency: str = "RUB") -> Optional[float]:
    """
    Получает текущий курс валюты через внешнее API.

    Args:
        from_currency: Исходная валюта (USD, EUR)
        to_currency: Целевая валюта (по умолчанию RUB)

    Returns:
        Курс обмена или None в случае ошибки
    """
    api_key = os.getenv('EXCHANGE_RATE_API_KEY')
    if not api_key:
        raise ValueError("API key not found in environment variables")

    url = f"https://api.apilayer.com/exchangerates_data/latest"

    try:
        response = requests.get(
            url,
            params={'base': from_currency, 'symbols': to_currency},
            headers={'apikey': api_key},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            return data['rates'].get(to_currency)
        else:
            return None

    except (requests.RequestException, KeyError):
        return None


def convert_amount_to_rub(transaction: Dict[str, Any]) -> float:
    """
    Конвертирует сумму транзакции в рубли.

    Args:
        transaction: Словарь с данными о транзакции

    Returns:
        Сумма транзакции в рублях (float)

    Raises:
        ValueError: Если не удалось получить курс валюты
    """
    operation_amount = transaction.get('operationAmount', {})
    amount_str = operation_amount.get('amount', '0')
    currency_info = operation_amount.get('currency', {})
    currency_code = currency_info.get('code', 'RUB')

    try:
        amount = float(amount_str)
    except (ValueError, TypeError):
        return 0.0

    # Если валюта уже рубли, возвращаем как есть
    if currency_code == 'RUB':
        return amount

    # Если валюта USD или EUR, конвертируем
    if currency_code in ['USD', 'EUR']:
        exchange_rate = get_exchange_rate(currency_code, 'RUB')
        if exchange_rate is not None:
            return amount * exchange_rate
        else:
            raise ValueError(f"Could not get exchange rate for {currency_code}")

    # Для других валют возвращаем 0 (или можно добавить обработку)
    return 0.0