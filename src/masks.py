def get_mask_card_number(card_number: str) -> str:
    """Маскирует номер карты в формате XXXX XX** **** XXXX."""
    if not isinstance(card_number, str) or not card_number.isdigit() or len(card_number) != 16:
        raise ValueError("Номер карты должен быть строкой из 16 цифр")

    return f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"


def get_mask_account(account_number: str) -> str:
    """Маскирует номер счёта в формате **XXXX."""
    if not isinstance(account_number, str) or not account_number.isdigit() or len(account_number) < 4:
        raise ValueError("Номер счёта должен быть строкой с минимум 4 цифрами")

    return f"**{account_number[-4:]}"
