import logging
import random

import streamlit as st

from logic_utils import check_guess, get_range_for_difficulty, parse_guess, update_score

# Standard logging replaces rich.Console for debug output
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

# ── Sidebar: difficulty selector ─────────────────────────────────────────────
# Player picks difficulty before or during a game; changing it resets state.
st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

# Map each difficulty to a maximum number of allowed attempts
attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

# Fetch the valid guess range for the selected difficulty
low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# ── Session state initialisation ─────────────────────────────────────────────
# Streamlit reruns the entire script on every interaction, so persistent values
# must live in st.session_state. These blocks only run on the very first load.
if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)
    st.session_state.difficulty = difficulty

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# ── Difficulty change detection ───────────────────────────────────────────────
# If the player switched difficulty mid-game, reset everything so the new range
# and attempt limit apply to a fresh round.
if st.session_state.get("difficulty") != difficulty:
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.difficulty = difficulty
    log.debug("Difficulty changed to %s; game state reset.", difficulty)

# ── Main game UI ──────────────────────────────────────────────────────────────
st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {max(0, attempt_limit - st.session_state.attempts)}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}",
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# ── New game handler ──────────────────────────────────────────────────────────
if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    log.debug("New game started at difficulty %s with range %d-%d.", difficulty, low, high)
    st.success("New game started.")
    st.rerun()

# ── Block further input if game is already over ───────────────────────────────
if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

# ── Submit guess handler ──────────────────────────────────────────────────────
if submit:
    # Parse and range-validate the raw text input
    ok, guess_int, err = parse_guess(raw_guess, low=low, high=high)

    if not ok:
        # Input was invalid (empty, non-integer, or out of range)
        log.debug("Rejected guess input: %r — %s", raw_guess, err)
        st.error(err)
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # Evaluate the guess against the hidden secret number
        outcome, message = check_guess(guess_int, st.session_state.secret)
        log.debug(
            "Guess #%d: %d vs secret %d → %s",
            st.session_state.attempts, guess_int, st.session_state.secret, outcome,
        )

        if show_hint:
            st.warning(message)

        # Update the running score based on outcome and attempt count
        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        elif st.session_state.attempts >= attempt_limit:
            # Player used all their attempts without guessing correctly
            st.session_state.status = "lost"
            st.error(
                f"Out of attempts! "
                f"The secret was {st.session_state.secret}. "
                f"Score: {st.session_state.score}"
            )

st.divider()
st.caption("Built by an AI that claims this code is production-ready. Fixed by a human that knows better than to trust a strange robot.")
