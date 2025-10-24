def is_valid_amount(amount):
    try:
        amount = float(amount)
        return amount > 0
    except ValueError:
        return False

def is_valid_date(date_str):
    from datetime import datetime
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def is_valid_category(category, valid_categories):
    return category in valid_categories

def validate_transaction(amount, date, category, valid_categories):
    if not is_valid_amount(amount):
        return False, "Invalid amount. It must be a positive number."
    if not is_valid_date(date):
        return False, "Invalid date. It must be in YYYY-MM-DD format."
    if not is_valid_category(category, valid_categories):
        return False, f"Invalid category. Valid categories are: {', '.join(valid_categories)}."
    return True, "Transaction is valid."