import logging
from .logger_config import setup_logger

# Создаем логгер для модуля masks
logger = setup_logger('masks', 'masks.log')


def get_mask_card_number(card_number: str) -> str:
    """Маскирует номер карты в формате XXXX XX** **** XXXX."""
    logger.debug(f"Попытка маскировки номера карты: {card_number}")

    if not isinstance(card_number, str) or not card_number.isdigit() or len(card_number) != 16:
        logger.error(f"Номер карты должен быть строкой из 16 цифр. Получено: {card_number}")
        raise ValueError("Номер карты должен быть строкой из 16 цифр")

    masked_card = f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"
    logger.info(f"Успешно замаскирован номер карты: {card_number} -> {masked_card}")
    return masked_card


def get_mask_account(account_number: str) -> str:
    """Маскирует номер счёта в формате **XXXX."""
    logger.debug(f"Попытка маскировки номера счета: {account_number}")

    if not isinstance(account_number, str) or not account_number.isdigit() or len(account_number) < 4:
        logger.error(f"Номер счёта должен быть строкой с минимум 4 цифрами. Получено: {account_number}")
        raise ValueError("Номер счёта должен быть строкой с минимум 4 цифрами")

    masked_account = f"**{account_number[-4:]}"
    logger.info(f"Успешно замаскирован номер счета: {account_number} -> {masked_account}")
    return masked_account