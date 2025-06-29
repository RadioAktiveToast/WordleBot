import random
import requests
from bs4 import BeautifulSoup

VOWELS = set('aeiou')

def fetch_word_list():
    print("🔄 Downloading Wordle word list...")
    url = "https://www.wordunscrambler.net/word-list/wordle-word-list"
    try:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        words = []

        for li in soup.select("li"):
            word = li.text.strip().lower()
            if len(word) == 5 and word.isalpha():
                words.append(word)

        unique_words = sorted(set(words))
        print(f"✅ Loaded {len(unique_words)} valid 5-letter words.")
        return unique_words

    except Exception as e:
        print("❌ Failed to download word list:", e)
        return []

def get_feedback(guess, solution):
    feedback = []
    solution_letters = list(solution)
    guess_letters = list(guess)

    # First pass for greens
    for i in range(5):
        if guess_letters[i] == solution_letters[i]:
            feedback.append('🟩')
            solution_letters[i] = None
        else:
            feedback.append(None)

    # Second pass for yellows and greys
    for i in range(5):
        if feedback[i] is None:
            if guess_letters[i] in solution_letters:
                feedback[i] = '🟨'
                solution_letters[solution_letters.index(guess_letters[i])] = None
            else:
                feedback[i] = '⬜'

    return ''.join(feedback)

def analyze_guess(guess, solution):
    feedback = get_feedback(guess, solution)
    green = feedback.count('🟩')
    yellow = feedback.count('🟨')

    if green == 5:
        comment = "Correct!"
    elif green >= 3:
        comment = "Hot guess!"
    elif yellow >= 3:
        comment = "You're circling it."
    elif green + yellow == 0:
        comment = "Cold guess."
    else:
        comment = "Decent try."

    return feedback, comment

def check_guess_quality(guess):
    if len(set(guess)) == 1:
        return "⚠️ All letters are the same."
    elif set(guess).issuperset(VOWELS):
        return "⚠️ All vowels used in one word."
    return ""

def compute_scores(guesses, solution):
    unique_letters_used = set()
    repeated_bad_letters = 0
    all_feedback = []

    for guess in guesses:
        feedback = get_feedback(guess, solution)
        all_feedback.append(feedback)
        for i, ch in enumerate(guess):
            if feedback[i] == '⬜':
                if ch in unique_letters_used:
                    repeated_bad_letters += 1
                unique_letters_used.add(ch)

    base_skill = max(0, 99 - len(guesses) * 10 - repeated_bad_letters * 2)
    skill_score = min(99, base_skill + 10)

    early_feedback = all_feedback[:2]
    early_points = sum(f.count('🟩') + f.count('🟨') for f in early_feedback)
    luck_score = min(99, 30 + early_points * 10 + random.randint(-5, 5))

    return max(skill_score, 10), max(min(luck_score, 99), 5)

def bot_guess_sequence(solution, word_list):
    print("\n🤖 Bot Simulation (Starting with CRANE):")
    possible_words = word_list[:]
    guesses = []
    guess = "crane"

    while True:
        feedback = get_feedback(guess, solution)
        guesses.append(guess)
        print(f"  ➤ {guess.upper()} {feedback}")
        if feedback == '🟩🟩🟩🟩🟩':
            break

        def match_feedback(word):
            return get_feedback(guess, word) == feedback

        possible_words = [word for word in possible_words if match_feedback(word)]
        guess = possible_words[0] if possible_words else "?????"

    print(f"🤖 Bot solved it in {len(guesses)} guesses!\n")

def wordlebot_game():
    word_list = fetch_word_list()
    if not word_list:
        print("Exiting because word list could not be loaded.")
        return

    print("🎯 WordleBot Analyzer 🎯")
    solution = input("Enter the correct 5-letter Wordle word: ").lower()
    while len(solution) != 5 or not solution.isalpha():
        solution = input("Word must be 5 letters. Try again: ").lower()

    guesses = []
    print("\nStart entering your guesses (press enter on empty line to finish):")
    while True:
        guess = input(f"Guess {len(guesses)+1}: ").lower()
        if not guess:
            break
        if len(guess) != 5 or not guess.isalpha():
            print("Invalid word. Must be 5 letters.")
            continue
        if guess not in word_list:
            print("❌ Not in valid word list.")
            continue

        warning = check_guess_quality(guess)
        if warning:
            print(f"  {warning}")

        guesses.append(guess)
        feedback, comment = analyze_guess(guess, solution)
        print(f"  ➤ {guess.upper()}  {feedback} — {comment}")
        if guess == solution:
            break

    print("\n🧠 Game Summary 🧠")
    print(f"Solution: {solution.upper()}")
    print(f"Total guesses: {len(guesses)}")

    skill, luck = compute_scores(guesses, solution)
    print(f"🎓 Skill: {skill}/99")
    print(f"🍀 Luck:  {luck}/99")
    print("Thanks for playing!")

    bot_guess_sequence(solution, word_list)

# Run the game
if __name__ == "__main__":
    wordlebot_game()
