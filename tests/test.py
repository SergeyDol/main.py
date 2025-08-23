def mask_account_card(account_info: str) -> str:
    """Маскирует номер карты или счета в переданной строке."""
    parts = account_info.split()
    if not parts:
        return account_info

    # Определяем, является ли последняя часть номером (состоит из цифр)
    number_part = parts[-1]
    if not number_part.isdigit():
        return account_info  # Если последняя часть не цифры, возвращаем как есть

    name_part = " ".join(parts[:-1]).lower()

    if not name_part or "счет" in name_part:
        # Маскировка для счета (если тип не указан или указан "счет")
        masked_number = "**" + number_part[-4:]
    else:
        # Маскировка для карты (если тип указан и это не "счет")
        if len(number_part) != 16:
            return account_info  # Некорректная длина номера карты
        masked_number = number_part[:4] + " " + number_part[4:6] + "** **** " + number_part[-4:]

    # Убираем лишний пробел, если name_part пустой
    return f"{name_part.capitalize()} {masked_number}".strip() if name_part else masked_number


print(mask_account_card("7000792289606361"))
print(mask_account_card("73654108430135874305"))
print(mask_account_card("Счет 73654108430135874305"))
print(mask_account_card("Visa 7000792289606361"))
