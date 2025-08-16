def get_mask_card_number(card_number: int) -> str:
    """Маскирует номер карты в формате XXXX XX** **** XXXX."""
    if not card_number.isdigit() or len(card_number) != 16:
        raise ValueError("Номер карты должен состоять из 16 цифр")

    masked_part = "** ****"
    return f"{card_number[:4]} {card_number[4:6]}{masked_part} {card_number[-4:]}"


def get_mask_account(account_number: int) -> str:
    """Маскирует номер счёта в формате **XXXX."""
    if not account_number.isdigit() or len(account_number) < 4:
        raise ValueError("Номер счёта должен содержать минимум 4 цифры")

    return f"**{account_number[-4:]}"
