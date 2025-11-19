def mask_account_card(account_info: str) -> str:
    """Маскирует номер карты или счета в переданной строке."""
    if not account_info or not isinstance(account_info, str):
        return account_info or ""

    # Если вся строка состоит из 16 цифр - это номер карты
    if account_info.isdigit() and len(account_info) == 16:
        return f"{account_info[:4]} {account_info[4:6]}** **** {account_info[-4:]}"

    parts = account_info.split()
    if not parts:
        return account_info

    number_part = parts[-1]

    # Если последняя часть не состоит из цифр, возвращаем как есть
    if not number_part.isdigit():
        return account_info

    name_part = " ".join(parts[:-1])

    # Определяем тип на основе названия
    if name_part:
        if any(keyword in name_part.lower() for keyword in ["счет", "account"]):
            # Это счет
            if len(number_part) >= 4:
                return f"{name_part} **{number_part[-4:]}"
            return account_info
        else:
            # Это карта
            if len(number_part) == 16:
                return f"{name_part} {number_part[:4]} {number_part[4:6]}** **** {number_part[-4:]}"
            return account_info
    else:
        # Если нет названия, определяем по длине номера
        if len(number_part) == 16:
            return f"{number_part[:4]} {number_part[4:6]}** **** {number_part[-4:}"
            elif len(number_part) >= 4:
            return f"**{number_part[-4:]}"
        return account_info


def get_date(date_string: str) -> str:
    """Преобразует дату из формата 'YYYY-MM-DDThh:mm:ss.ssssss' в 'DD.MM.YYYY'."""
    from datetime import datetime

    if not date_string or not isinstance(date_string, str):
        return ""

    try:
        clean_date = date_string.replace("Z", "+00:00")
        date_object = datetime.fromisoformat(clean_date)
        return date_object.strftime("%d.%m.%Y")
    except (ValueError, TypeError):
        return date_string