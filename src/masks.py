import logging
from src.logger_config import setup_logger

# Создаем логгер для модуля masks
logger = setup_logger("masks", "masks.log")


def get_mask_card_number(card_number: str) -> str:
    """Маскирует номер карты в формате XXXX XX** **** XXXX."""
    logger.debug(f"Попытка маскирования номера карты: {card_number[:4]}...{card_number[-4:] if len(card_number) > 4 else ''}")

    if not isinstance(card_number, str) or not card_number.isdigit() or len(card_number) != 16:
        error_msg = "Номер карты должен быть строкой из 16 цифр"
        logger.error(error_msg)
        raise ValueError(error_msg)

    masked = f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"
    logger.info(f"Успешно замаскирован номер карты: {masked}")
    return masked


def get_mask_account(account_number: str) -> str:
    """Маскирует номер счёта в формате **XXXX."""
    logger.debug(f"Попытка маскирования номера счета: ...{account_number[-4:] if len(account_number) > 4 else account_number}")

    if not isinstance(account_number, str) or not account_number.isdigit() or len(account_number) < 4:
        logger.error(f"Ошибка: некорректный номер счета - {account_number}")
        raise ValueError("Номер счёта должен быть строкой с минимум 4 цифрами")

    masked = f"**{account_number[-4:]}"
    logger.info(f"Успешно замаскирован номер счета: {masked}")
    return masked