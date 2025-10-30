import os
import tempfile

import pytest

from src.decorators import log


class TestLogDecorator:
    """Тесты для декоратора log"""

    def test_log_to_console_success(self, capsys):
        """Тестирование логирования успешного выполнения в консоль"""

        @log()
        def add(a, b):
            return a + b

        result = add(1, 2)

        # Проверяем результат
        assert result == 3

        # Проверяем вывод в консоль
        captured = capsys.readouterr()
        assert "add ok" in captured.out
        assert "error" not in captured.out

    def test_log_to_console_error(self, capsys):
        """Тестирование логирования ошибки в консоль"""

        @log()
        def divide(a, b):
            return a / b

        # Проверяем, что исключение пробрасывается
        with pytest.raises(ZeroDivisionError):
            divide(1, 0)

        # Проверяем вывод в консоль
        captured = capsys.readouterr()
        assert "divide error: ZeroDivisionError" in captured.out
        assert "Inputs: (1, 0), {}" in captured.out

    def test_log_to_file_success(self):
        """Тестирование логирования успешного выполнения в файл"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_filename = temp_file.name

        try:

            @log(filename=temp_filename)
            def multiply(a, b):
                return a * b

            result = multiply(3, 4)

            # Проверяем результат
            assert result == 12

            # Проверяем запись в файл
            with open(temp_filename, "r", encoding="utf-8") as f:
                content = f.read()
                assert "multiply ok" in content
                assert "error" not in content

        finally:
            # Удаляем временный файл
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_log_to_file_error(self):
        """Тестирование логирования ошибки в файл"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_filename = temp_file.name

        try:

            @log(filename=temp_filename)
            def raise_value_error():
                raise ValueError("Test error")

            # Проверяем, что исключение пробрасывается
            with pytest.raises(ValueError):
                raise_value_error()

            # Проверяем запись в файл
            with open(temp_filename, "r", encoding="utf-8") as f:
                content = f.read()
                assert "raise_value_error error: ValueError" in content
                assert "Inputs: (), {}" in content

        finally:
            # Удаляем временный файл
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_log_with_keyword_args(self, capsys):
        """Тестирование логирования с keyword arguments"""

        @log()
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = greet("Alice", greeting="Hi")

        # Проверяем результат
        assert result == "Hi, Alice!"

        # Проверяем вывод в консоль
        captured = capsys.readouterr()
        assert "greet ok" in captured.out

    def test_log_preserves_function_metadata(self):
        """Тестирование, что декоратор сохраняет метаданные функции"""

        @log()
        def test_func(a: int, b: int) -> int:
            """Test function for metadata preservation."""
            return a + b

        # Проверяем сохранение метаданных
        assert test_func.__name__ == "test_func"
        assert test_func.__doc__ == "Test function for metadata preservation."
        assert test_func.__annotations__ == {"a": int, "b": int, "return": int}

    def test_log_without_filename_and_with_filename(self, capsys):
        """Тестирование смешанного использования (с filename и без)"""
        # Создаем временный файл для второго теста
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_filename = temp_file.name

        try:
            # Функция с выводом в консоль
            @log()
            def console_func(x):
                return x * 2

            # Функция с выводом в файл
            @log(filename=temp_filename)
            def file_func(y):
                return y + 1

            # Вызываем обе функции
            console_result = console_func(5)
            file_result = file_func(10)

            # Проверяем результаты
            assert console_result == 10
            assert file_result == 11

            # Проверяем вывод в консоль (только от console_func)
            captured = capsys.readouterr()
            assert "console_func ok" in captured.out
            assert "file_func" not in captured.out  # file_func пишет в файл, не в консоль

            # Проверяем запись в файл (только от file_func)
            with open(temp_filename, "r", encoding="utf-8") as f:
                content = f.read()
                assert "file_func ok" in content
                assert "console_func" not in content  # console_func пишет в консоль, не в файл

        finally:
            # Удаляем временный файл
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
