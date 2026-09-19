"""
frequency_analysis.py — Cipher Breaking via Frequency Analysis
----------------------------------------------------------------
English letter frequency is well-known. By counting how often each letter
appears in a ciphertext, we can infer which cipher shift (Caesar) was most
likely used, because the distribution will mirror the English profile.

  Most common English letters: E T A O I N S H R D L C U M W F G Y P B V K J X Q Z

For Vigenère, we also compute the Index of Coincidence (IC) to detect whether
a given key length aligns the cipher into Caesar-like streams.
"""

from collections import Counter
from utils import cyan, yellow, green, dim, red, result_box, info


# ── English letter frequency profile (%) ─────────────────────────────────────
ENGLISH_FREQ = {
    'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97,
    'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25,
    'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36,
    'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.49,
    'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10,
    'Z': 0.07
}

SORTED_ENGLISH = [k for k, _ in sorted(ENGLISH_FREQ.items(),
                                        key=lambda x: x[1], reverse=True)]


# ── Core analysis functions ───────────────────────────────────────────────────

def letter_frequencies(text: str) -> dict[str, float]:
    """
    Compute the percentage frequency of each letter in text.

    Returns:
        dict mapping 'A'–'Z' → frequency percentage
    """
    text   = text.upper()
    letters = [c for c in text if c.isalpha()]
    total   = len(letters)
    if total == 0:
        return {chr(i + 65): 0.0 for i in range(26)}
    counts = Counter(letters)
    return {chr(i + 65): counts.get(chr(i + 65), 0) / total * 100
            for i in range(26)}


def chi_squared_score(observed: dict[str, float]) -> float:
    """
    Calculate how closely a frequency distribution matches English.
    Lower score = better match = more likely to be English plaintext.
    """
    score = 0.0
    for letter, expected_pct in ENGLISH_FREQ.items():
        observed_pct = observed.get(letter, 0)
        score += (observed_pct - expected_pct) ** 2 / (expected_pct + 1e-9)
    return score


def index_of_coincidence(text: str) -> float:
    """
    Compute the Index of Coincidence (IC) for text.
    English plaintext IC ≈ 0.065; random text IC ≈ 0.038.
    Higher IC → more likely the text is in a natural language.
    """
    text   = ''.join(c for c in text.upper() if c.isalpha())
    n      = len(text)
    if n < 2:
        return 0.0
    counts = Counter(text)
    return sum(f * (f - 1) for f in counts.values()) / (n * (n - 1))


def crack_caesar(ciphertext: str) -> list[tuple[int, float, str]]:
    """
    Attempt to crack a Caesar cipher by ranking all 25 shifts.
    Uses chi-squared scoring against the English frequency profile.

    Returns:
        List of (shift, score, decrypted_text) sorted best-first (lowest score).
    """
    from caesar import decrypt
    results = []
    for shift in range(1, 26):
        plaintext = decrypt(ciphertext, shift)
        freq      = letter_frequencies(plaintext)
        score     = chi_squared_score(freq)
        results.append((shift, score, plaintext))
    return sorted(results, key=lambda x: x[1])


def crack_vigenere_column(column_text: str) -> tuple[int, str]:
    """
    Crack a single column of a Vigenère ciphertext using Caesar brute-force.
    Returns (best_shift, key_letter).
    """
    from caesar import decrypt
    best_shift = 0
    best_score = float('inf')
    for shift in range(26):
        plain = decrypt(column_text, shift)
        freq  = letter_frequencies(plain)
        score = chi_squared_score(freq)
        if score < best_score:
            best_score = shift
            best_shift = shift
    return best_shift, chr(best_shift + ord('A'))


def crack_vigenere(ciphertext: str, key_length: int) -> tuple[str, str]:
    """
    Attempt to crack a Vigenère cipher given an estimated key length.

    Returns:
        (guessed_key, decrypted_text)
    """
    from vigenere import decrypt
    import re

    text    = re.sub(r'[^A-Za-z]', '', ciphertext).upper()
    columns = [''.join(text[i::key_length]) for i in range(key_length)]
    key     = ''.join(crack_vigenere_column(col)[1] for col in columns)
    return key, decrypt(ciphertext, key)


def print_frequency_chart(text: str):
    """
    Print an ASCII bar chart of letter frequencies in the text.
    """
    freq = letter_frequencies(text)
    max_freq = max(freq.values()) if freq.values() else 1
    scale = 40 / max_freq if max_freq > 0 else 1

    print(f"\n  {yellow('Letter Frequency Analysis:')}\n")
    for letter in 'ETAOINSHRDLCUMWFGYPBVKJXQZ':
        pct    = freq[letter]
        bar_w  = int(pct * scale)
        eng_w  = int(ENGLISH_FREQ.get(letter, 0) * scale)
        bar    = "█" * bar_w
        color  = green if pct >= ENGLISH_FREQ.get(letter, 0) - 2 else red
        print(f"    {cyan(letter)} │{color(bar):<42} {dim(f'{pct:5.2f}%')}")
    print()
    print(f"  {dim('Legend: higher bars = more frequent letters')}")


# ── Interactive menu handler ──────────────────────────────────────────────────

def menu():
    """Interactive sub-menu for frequency analysis operations."""
    from utils import section_header, prompt, prompt_int, pause, result_box, error

    while True:
        section_header("Frequency Analysis & Cipher Breaking")
        print(f"  {cyan('1.')} Show letter frequency chart of any text")
        print(f"  {cyan('2.')} Crack Caesar cipher (auto-detect shift)")
        print(f"  {cyan('3.')} Crack Vigenère cipher (provide key length)")
        print(f"  {cyan('4.')} Index of Coincidence calculator")
        print(f"  {cyan('0.')} Back to main menu")

        choice = prompt("Select option")

        if choice == "1":
            text = prompt("Enter text to analyze")
            print_frequency_chart(text)
            pause()

        elif choice == "2":
            text    = prompt("Enter Caesar ciphertext")
            results = crack_caesar(text)
            print(f"\n  {yellow('Top 5 most likely decryptions:')}\n")
            for rank, (shift, score, plain) in enumerate(results[:5], 1):
                marker = green("★ BEST") if rank == 1 else dim(f"  #{rank}")
                print(f"  {marker}  Shift {cyan(str(shift)):>4}  →  {plain}")
            print()
            best_shift, _, best_plain = results[0]
            result_box(f"Most likely (shift={best_shift}):", best_plain)
            pause()

        elif choice == "3":
            text    = prompt("Enter Vigenère ciphertext")
            key_len = prompt_int("Enter estimated key length (from Kasiski)", 1, 20)
            key, plain = crack_vigenere(text, key_len)
            result_box(f"Guessed key: {key}", plain)
            pause()

        elif choice == "4":
            text = prompt("Enter text to measure")
            ic   = index_of_coincidence(text)
            print()
            result_box("Index of Coincidence:", f"{ic:.4f}")
            if ic >= 0.060:
                info("IC ≈ 0.065 → Likely English plaintext or Caesar cipher")
            elif ic >= 0.045:
                info("IC between 0.045–0.060 → Possibly Vigenère with short key")
            else:
                info("IC ≈ 0.038 → Likely random or long-key Vigenère cipher")
            pause()

        elif choice == "0":
            break

        else:
            error("Invalid option. Choose 0–4.")
            pause()
