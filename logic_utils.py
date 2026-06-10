def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    ranges = {
        "Easy": (1, 20),
        "Normal": (1, 50),
        "Hard": (1, 100),
    }
    if difficulty not in ranges:
        raise ValueError(f"Unknown difficulty: {difficulty!r}")
    return ranges[difficulty]


def parse_guess(raw: str, low: int = None, high: int = None):
    """
    Parse and validate user input into an integer guess.

    Steps:
      1. Reject empty/None input immediately.
      2. Attempt integer conversion — rejects decimals and non-numeric strings.
      3. If low/high bounds are provided, reject values outside the current range.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    # Step 1: reject blank input
    if raw is None:
        return False, None, "Enter a guess."

    text = str(raw).strip()
    if text == "":
        return False, None, "Enter a guess."

    # Step 2: parse to integer (rejects decimals like "42.5")
    try:
        value = int(text)
    except (TypeError, ValueError):
        return False, None, "That is not a number."

    # Step 3: range check (only enforced when bounds are passed in)
    if low is not None and high is not None:
        if value < low or value > high:
            return False, None, f"Guess must be between {low} and {high}."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    Outcomes: "Win", "Too High", "Too Low"
    """
    # Exact match — player wins
    if guess == secret:
        return "Win", "🎉 Correct!"

    # Guess is above the secret — tell player to go lower
    if guess > secret:
        return "Too High", "📉 Go LOWER!"

    # Guess is below the secret — tell player to go higher
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """
    Adjust score based on the outcome of a guess.

    Wins award points that decrease with each attempt (min 10).
    Wrong guesses deduct 5 points per attempt.
    """
    if outcome == "Win":
        # Reward fewer attempts with a higher score, floored at 10
        points = max(10, 110 - 10 * attempt_number)
        return current_score + points

    if outcome in {"Too High", "Too Low"}:
        # Small penalty for each wrong guess
        return current_score - 5

    return current_score
