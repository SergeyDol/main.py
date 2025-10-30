import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name: str, log_file: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    Настраивает и возвращает логгер для модуля.
    """
    # Создаем логгер
    logger = logging.getLogger(name)

    # Установлен уровень логирования не меньше, чем DEBUG
    logger.setLevel(level)  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # Проверяем, что у логгера еще нет handlers
    if logger.handlers:
        return logger

    # Создаем папку logs если ее нет
    os.makedirs("logs", exist_ok=True)

    # Настроен file_handler для логера
    file_handler = RotatingFileHandler(
        f"logs/{log_file}",  # Файлы логов с расширением .log
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)

    # Настроен file_formatter для логера
    # Формат записи логов включает метку времени, название модуля, уровень серьезности и сообщение
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Время - модуль - уровень - сообщение
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Установлен форматер для логера
    file_handler.setFormatter(file_formatter)

    # Добавлен handler для логера
    logger.addHandler(file_handler)

    return logger
