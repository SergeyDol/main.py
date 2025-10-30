import json
import os
import tempfile

import pytest

from src.utils import read_json_file


class TestUtils:
    """Тесты для модуля utils"""

    def test_read_json_file_valid(self):
        """Тестирование чтения корректного JSON файла"""
        # Создаем временный файл с корректными данными
        test_data = [{"id": 1, "amount": "100.50"}, {"id": 2, "amount": "200.75"}]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name

        try:
            result = read_json_file(temp_path)
            assert result == test_data
        finally:
            os.unlink(temp_path)

    def test_read_json_file_not_list(self):
        """Тестирование чтения JSON файла, который не содержит список"""
        test_data = {"id": 1, "amount": "100.50"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name

        try:
            result = read_json_file(temp_path)
            assert result == []
        finally:
            os.unlink(temp_path)

    def test_read_json_file_not_found(self):
        """Тестирование чтения несуществующего файла"""
        result = read_json_file("nonexistent_file.json")
        assert result == []

    def test_read_json_file_invalid_json(self):
        """Тестирование чтения некорректного JSON файла"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name

        try:
            result = read_json_file(temp_path)
            assert result == []
        finally:
            os.unlink(temp_path)

    def test_read_json_file_empty(self):
        """Тестирование чтения пустого файла"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            result = read_json_file(temp_path)
            assert result == []
        finally:
            os.unlink(temp_path)
