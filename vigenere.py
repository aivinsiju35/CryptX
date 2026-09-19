"""
vigenere.py — Vigenère Cipher Implementation
----------------------------------------------
The Vigenère cipher uses a keyword to apply a different Caesar shift to each
letter of the plaintext. This makes it a *polyalphabetic* substitution cipher.

  For each letter at position i:
    Encrypt: C[i] = (P[i] + key[i % len(key)]) mod 26
    Decrypt: P[i] = (C[i] - key[i % len(key)]) mod 26

Key can only contain letters (a–z / A–Z); case is ignored.
"""

import re
from utils import cyan, yellow, dim, result_box, info, error


# ── Validation ────────────────────────────────────────────────────────────────

def _validate_key(key: str) -> str:
    """Return cleaned uppercase key or raise ValueError if invalid."""
    key = key.strip().upper()
    if not key.isalpha():
        raise ValueError("Vigenère key must contain only letters (a–z).")
    return key


# ── Core cipher functions ─────────────────────────────────────────────────────

def encrypt(text: str, key: str) -> str:
    """
    Encrypt plaintext using the Vigenère cipher.

    Args:
        text : plaintext string
        key  : keyword (letters only)

    Returns:
        Ciphertext string.
    """
    key = _validate_key(key)
    result = []
    key_idx = 0
    for char in text:
        if char.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('A')
            base  = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base + shift) % 26 + base))
            key_idx += 1
        else:
            result.append(char)
    return "".join(result)


def decrypt(text: str, key: str) -> str:
    """
    Decrypt ciphertext encrypted with the Vigenère cipher.

    Args:
        text : ciphertext string
        key  : keyword used during encryption

    Returns:
        Plaintext string.
    """
    key = _validate_key(key)
    result = []
    key_idx = 0
    for char in text:
        if char.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('A')
            base  = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base - shift) % 26 + base))
            key_idx += 1
        else:
            result.append(char)
    return "".join(result)


def kasiski_key_length_hint(ciphertext: str) -> list[int]:
    """
    Estimate likely key lengths using the Kasiski examination.
    Finds repeated trigrams and measures distances between them.
    The GCD of those distances often reveals the key length.

    Returns:
        Sorted list of candidate key lengths (most likely first).
    """
    import math
    from collections import Counter

    text = re.sub(r'[^A-Za-z]', '', ciphertext).upper()
    distances = []

    for length in range(3, 6):          # Look for repeated n-grams (3-5 chars)
        seen = {}
        for i in range(len(text) - length):
            gram = text[i:i + length]
            if gram in seen:
                distances.append(i - seen[gram])
            seen[gram] = i

    if not distances:
        return []

    # Count common GCDs of distances
    gcd_counts = Counter()
    for d in distances:
        for length in range(2, 13):
            if d % length == 0:
                gcd_counts[length] += 1

    # Return top 5 candidates sorted by frequency
    return [k for k, _ in gcd_counts.most_common(5)]


# ── Interactive menu handler ──────────────────────────────────────────────────

def menu():
    """Interactive sub-menu for Vigenère cipher operations."""
    from utils import section_header, prompt, pause, result_box

    while True:
        section_header("Vigenère Cipher")
        print(f"  {cyan('1.')} Encrypt text")
        print(f"  {cyan('2.')} Decrypt text")
        print(f"  {cyan('3.')} Kasiski key-length hint (help crack it)")
        print(f"  {cyan('0.')} Back to main menu")

        choice = prompt("Select option")

        if choice == "1":
            text = prompt("Enter plaintext")
            key  = prompt("Enter keyword (letters only)")
            try:
                ct = encrypt(text, key)
                result_box("Ciphertext:", ct)
                info(f"Keyword used: {key.upper()}")
            except ValueError as e:
                error(str(e))
            pause()

        elif choice == "2":
            text = prompt("Enter ciphertext")
            key  = prompt("Enter keyword (letters only)")
            try:
                pt = decrypt(text, key)
                result_box("Plaintext:", pt)
            except ValueError as e:
                error(str(e))
            pause()

        elif choice == "3":
            text = prompt("Enter ciphertext (longer texts give better hints)")
            hints = kasiski_key_length_hint(text)
            if hints:
                print(f"\n  {yellow('Likely key lengths (most probable first):')}")
                for i, kl in enumerate(hints, 1):
                    print(f"    {dim(str(i)+'.')}  Key length ≈ {cyan(str(kl))}")
            else:
                info("Not enough repeated patterns found. Try a longer ciphertext.")
            pause()

        elif choice == "0":
            break

        else:
            error("Invalid option. Choose 0–3.")
            pause()
