import os
import tempfile

import pandas as pd
import pytest

from src.utils.file_operations import load_csv_transactions, load_excel_transactions


class TestFileOperations:
    """Тесты для операций с файлами с использованием pandas."""

    @pytest.fixture
    def sample_csv_data(self):
        """Фикстура с тестовыми данными для CSV."""
        return [
            {"id": 1, "date": "2023-01-01", "description": "Перевод", "amount": 1000},
            {"id": 2, "date": "2023-01-02", "description": "Пополнение", "amount": 500},
            {"id": 3, "date": "2023-01-03", "description": "Списание", "amount": 200},
        ]

    @pytest.fixture
    def sample_excel_data(self):
        """Фикстура с тестовыми данными для Excel."""
        return [
            {"id": 1, "date": "2023-01-01", "description": "Перевод", "amount": 1000},
            {"id": 2, "date": "2023-01-02", "description": "Пополнение", "amount": 500},
            {"id": 3, "date": "2023-01-03", "description": "Списание", "amount": 200},
        ]

    def test_load_csv_transactions_success(self, sample_csv_data):
        """Тест успешной загрузки CSV файла."""
        # Создаем временный CSV файл
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df = pd.DataFrame(sample_csv_data)
            df.to_csv(f.name, index=False)
            temp_path = f.name

        try:
            result = load_csv_transactions(temp_path)
            assert len(result) == 3
            assert result[0]["description"] == "Перевод"
            assert result[1]["amount"] == 500
        finally:
            os.unlink(temp_path)

    def test_load_csv_transactions_file_not_found(self):
        """Тест загрузки несуществующего CSV файла."""
        result = load_csv_transactions("nonexistent.csv")
        assert result == []

    def test_load_excel_transactions_success(self, sample_excel_data):
        """Тест успешной загрузки Excel файла."""
        # Создаем временный Excel файл
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".xlsx", delete=False) as f:
            df = pd.DataFrame(sample_excel_data)
            df.to_excel(f.name, index=False)
            temp_path = f.name

        try:
            result = load_excel_transactions(temp_path)
            assert len(result) == 3
            assert result[0]["description"] == "Перевод"
            assert result[1]["amount"] == 500
        finally:
            os.unlink(temp_path)

    def test_load_excel_transactions_file_not_found(self):
        """Тест загрузки несуществующего Excel файла."""
        result = load_excel_transactions("nonexistent.xlsx")
        assert result == []
