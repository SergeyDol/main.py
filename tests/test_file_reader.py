import os
import tempfile
from unittest.mock import MagicMock, patch

import pandas as pd

from src.file_reader import detect_file_type_and_read, read_csv_file, read_excel_file


class TestFileReader:
    """Тесты для модуля file_reader"""

    def test_read_csv_file_success(self):
        """Тестирование успешного чтения CSV файла"""
        # Создаем временный CSV файл
        test_data = [
            {"id": 1, "amount": "100.50", "currency": "RUB"},
            {"id": 2, "amount": "200.75", "currency": "USD"},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df = pd.DataFrame(test_data)
            df.to_csv(f.name, index=False)
            temp_path = f.name

        try:
            result = read_csv_file(temp_path)
            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[1]["id"] == 2
        finally:
            os.unlink(temp_path)

    @patch("src.file_reader.pd.read_csv")
    def test_read_csv_file_with_mock(self, mock_read_csv):
        """Тестирование чтения CSV файла с использованием Mock"""
        # Настраиваем mock
        mock_df = MagicMock()
        mock_df.to_dict.return_value = [{"id": 1, "amount": "100.50"}, {"id": 2, "amount": "200.75"}]
        mock_read_csv.return_value = mock_df

        result = read_csv_file("test.csv")

        assert len(result) == 2
        mock_read_csv.assert_called_once_with("test.csv")
        mock_df.to_dict.assert_called_once_with("records")

    def test_read_csv_file_not_found(self):
        """Тестирование чтения несуществующего CSV файла"""
        result = read_csv_file("nonexistent.csv")
        assert result == []

    @patch("src.file_reader.pd.read_csv")
    def test_read_csv_file_empty(self, mock_read_csv):
        """Тестирование чтения пустого CSV файла"""
        mock_read_csv.side_effect = pd.errors.EmptyDataError

        result = read_csv_file("empty.csv")
        assert result == []

    def test_read_excel_file_success(self):
        """Тестирование успешного чтения Excel файла"""
        # Создаем временный Excel файл
        test_data = [
            {"id": 1, "amount": "100.50", "currency": "RUB"},
            {"id": 2, "amount": "200.75", "currency": "USD"},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xlsx", delete=False) as f:
            df = pd.DataFrame(test_data)
            df.to_excel(f.name, index=False)
            temp_path = f.name

        try:
            result = read_excel_file(temp_path)
            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[1]["id"] == 2
        finally:
            os.unlink(temp_path)

    @patch("src.file_reader.pd.read_excel")
    def test_read_excel_file_with_mock(self, mock_read_excel):
        """Тестирование чтения Excel файла с использованием Mock"""
        # Настраиваем mock
        mock_df = MagicMock()
        mock_df.to_dict.return_value = [{"id": 1, "amount": "100.50"}, {"id": 2, "amount": "200.75"}]
        mock_read_excel.return_value = mock_df

        result = read_excel_file("test.xlsx")

        assert len(result) == 2
        mock_read_excel.assert_called_once_with("test.xlsx", sheet_name=0)
        mock_df.to_dict.assert_called_once_with("records")

    def test_read_excel_file_not_found(self):
        """Тестирование чтения несуществующего Excel файла"""
        result = read_excel_file("nonexistent.xlsx")
        assert result == []

    @patch("src.file_reader.pd.read_excel")
    def test_read_excel_file_invalid_sheet(self, mock_read_excel):
        """Тестирование чтения Excel файла с несуществующим листом"""
        mock_read_excel.side_effect = ValueError("Sheet not found")

        result = read_excel_file("test.xlsx", "invalid_sheet")
        assert result == []

    def test_detect_file_type_csv(self):
        """Тестирование определения типа файла для CSV"""
        with patch("src.file_reader.read_csv_file") as mock_read_csv:
            mock_read_csv.return_value = [{"test": "data"}]

            result = detect_file_type_and_read("test.csv")
            mock_read_csv.assert_called_once_with("test.csv")
            assert result == [{"test": "data"}]

    def test_detect_file_type_excel(self):
        """Тестирование определения типа файла для Excel"""
        with patch("src.file_reader.read_excel_file") as mock_read_excel:
            mock_read_excel.return_value = [{"test": "data"}]

            result = detect_file_type_and_read("test.xlsx")
            mock_read_excel.assert_called_once_with("test.xlsx")
            assert result == [{"test": "data"}]

    def test_detect_file_type_json(self):
        """Тестирование определения типа файла для JSON"""
        with patch("src.file_reader.read_json_file") as mock_read_json:
            mock_read_json.return_value = [{"test": "data"}]

            result = detect_file_type_and_read("test.json")
            mock_read_json.assert_called_once_with("test.json")
            assert result == [{"test": "data"}]

    def test_detect_file_type_unsupported(self):
        """Тестирование определения неподдерживаемого типа файла"""
        result = detect_file_type_and_read("test.txt")
        assert result == []
