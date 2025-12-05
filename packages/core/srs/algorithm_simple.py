def calculate_next_review(is_correct: bool, current_interval: int) -> int:
    return max(1, current_interval * 2) if is_correct else 1
