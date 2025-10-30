import logging
import os
import tempfile

import pytest

from src.masks import get_mask_account, get_mask_card_number
from src.utils import read_json_file


class TestLoggingRequirements:
    """Тесты для проверки выполнения всех требований логирования"""

    def test_utils_logger_has_correct_settings(self):
        """Проверка настроек логгера для модуля utils"""
        from src.utils import logger

        # Проверяем что логгер создан
        assert isinstance(logger, logging.Logger)
        assert logger.name == "utils"

        # Проверяем уровень логирования (не меньше DEBUG)
        assert logger.level <= logging.DEBUG

        # Проверяем наличие file handler
        assert len(logger.handlers) > 0
        assert any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)

    def test_masks_logger_has_correct_settings(self):
        """Проверка настроек логгера для модуля masks"""
        from src.masks import logger

        # Проверяем что логгер создан
        assert isinstance(logger, logging.Logger)
        assert logger.name == "masks"

        # Проверяем уровень логирования (не меньше DEBUG)
        assert logger.level <= logging.DEBUG

        # Проверяем наличие file handler
        assert len(logger.handlers) > 0
        assert any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)

    def test_log_files_created(self):
        """Проверка создания файлов логов"""
        # Вызываем функции чтобы создать логи
        read_json_file("nonexistent.json")
        try:
            get_mask_card_number("123")
        except ValueError:
            pass

        # Проверяем что файлы логов создались
        assert os.path.exists("logs/utils.log")
        assert os.path.exists("logs/masks.log")

    def test_log_format_includes_required_fields(self):
        """Проверка формата логов"""
        # Генерируем лог
        read_json_file("nonexistent.json")

        # Читаем последнюю запись
        with open("logs/utils.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1]

                # Проверяем что формат включает все требуемые поля
                parts = last_line.strip().split(" - ")
                assert len(parts) >= 4

                # Метка времени (должна содержать дату и время)
                assert len(parts[0]) > 0

                # Название модуля
                assert parts[1] == "utils"

                # Уровень серьезности
                assert parts[2] in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

                # Сообщение
                assert len(parts[3]) > 0

    def test_utils_success_logging(self, tmp_path):
        """Проверка логирования успешных операций в utils"""
        # Создаем временный JSON файл
        test_data = [{"id": 1, "amount": "100.50"}]
        test_file = tmp_path / "test.json"
        import json

        with open(test_file, "w") as f:
            json.dump(test_data, f)

        # Читаем файл
        result = read_json_file(str(test_file))

        # Проверяем что операция прошла успешно
        assert result == test_data

        # Проверяем что в логе есть запись об успехе
        with open("logs/utils.log", "r", encoding="utf-8") as f:
            log_content = f.read()
            assert "Успешно прочитан JSON файл" in log_content
            assert "INFO" in log_content

    def test_utils_error_logging(self):
        """Проверка логирования ошибок в utils"""
        # Пытаемся прочитать несуществующий файл
        result = read_json_file("nonexistent_file.json")

        # Проверяем что вернулся пустой список
        assert result == []

        # Проверяем что в логе есть запись об ошибке с уровнем ERROR
        with open("logs/utils.log", "r", encoding="utf-8") as f:
            log_content = f.read()
            assert "Файл не найден" in log_content
            assert "ERROR" in log_content

    def test_masks_success_logging(self):
        """Проверка логирования успешных операций в masks"""
        # Маскируем корректный номер карты
        result = get_mask_card_number("1234567890123456")

        # Проверяем результат
        assert result == "1234 56** **** 3456"

        # Проверяем что в логе есть запись об успехе
        with open("logs/masks.log", "r", encoding="utf-8") as f:
            log_content = f.read()
            assert "Успешно замаскирован номер карты" in log_content
            assert "INFO" in log_content

    def test_masks_error_logging(self):
        """Проверка логирования ошибок в masks"""
        # Пытаемся маскировать некорректный номер карты
        with pytest.raises(ValueError):
            get_mask_card_number("123")

        # Проверяем что в логе есть запись об ошибке с уровнем ERROR
        with open("logs/masks.log", "r", encoding="utf-8") as f:
            log_content = f.read()
            assert "ERROR" in log_content
            assert "Номер карты должен быть строкой из 16 цифр" in log_content

    def test_logs_directory_created(self):
        """Проверка создания папки logs"""
        # Проверяем что папка logs существует
        assert os.path.exists("logs")
        assert os.path.isdir("logs")

    def test_log_files_have_log_extension(self):
        """Проверка что файлы логов имеют расширение .log"""
        # Проверяем расширения файлов
        assert "utils.log" in os.listdir("logs")
        assert "masks.log" in os.listdir("logs")
