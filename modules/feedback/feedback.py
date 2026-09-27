def validate_feedback(message, rating):
    if not message:
        return False

    if not isinstance(rating, int):
        return False

    if rating < 1 or rating > 5:
        return False

    return True