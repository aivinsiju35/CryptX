"""
caesar.py — Caesar Cipher Implementation
-----------------------------------------
The Caesar cipher shifts every letter in the plaintext by a fixed number
(the 'key' / shift value). Non-alphabetic characters are preserved as-is.

  Encrypt: C = (P + shift) mod 26
  Decrypt: P = (C - shift) mod 26
"""

from utils import green, red, cyan, yellow, dim, result_box, info


# ── Core cipher functions ─────────────────────────────────────────────────────

def encrypt(text: str, shift: int) -> str:
    """
    Encrypt plaintext using Caesar cipher.

    Args:
        text  : plaintext string (any characters)
        shift : integer shift value (0–25)

    Returns:
        Ciphertext string with letters shifted; other chars unchanged.
    """
    shift = shift % 26
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base + shift) % 26 + base))
        else:
            result.append(char)
    return "".join(result)


def decrypt(text: str, shift: int) -> str:
    """
    Decrypt ciphertext encrypted with a Caesar cipher.

    Args:
        text  : ciphertext string
        shift : the shift that was used during encryption

    Returns:
        Plaintext string.
    """
    return encrypt(text, -shift)


def brute_force(ciphertext: str) -> dict[int, str]:
    """
    Try all 25 possible Caesar shifts and return every decryption.

    Returns:
        dict mapping shift_value → decrypted_string
    """
    return {shift: decrypt(ciphertext, shift) for shift in range(1, 26)}


# ── Interactive menu handler ──────────────────────────────────────────────────

def menu():
    """Interactive sub-menu for Caesar cipher operations."""
    from utils import section_header, prompt, prompt_int, pause, result_box, error

    while True:
        section_header("Caesar Cipher")
        print(f"  {cyan('1.')} Encrypt text")
        print(f"  {cyan('2.')} Decrypt text")
        print(f"  {cyan('3.')} Brute-force all 25 shifts")
        print(f"  {cyan('0.')} Back to main menu")

        choice = prompt("Select option")

        if choice == "1":
            text  = prompt("Enter plaintext")
            shift = prompt_int("Enter shift value (1-25)", 1, 25)
            ciphertext = encrypt(text, shift)
            result_box("Ciphertext:", ciphertext)
            info(f"Shift used: {shift}")
            pause()

        elif choice == "2":
            text  = prompt("Enter ciphertext")
            shift = prompt_int("Enter shift value (1-25)", 1, 25)
            plaintext = decrypt(text, shift)
            result_box("Plaintext:", plaintext)
            pause()

        elif choice == "3":
            text = prompt("Enter ciphertext to brute-force")
            print()
            results = brute_force(text)
            print(f"  {yellow('All possible decryptions:')}\n")
            for shift, plain in results.items():
                print(f"  {dim(f'Shift {shift:>2}:')}  {plain}")
            pause()

        elif choice == "0":
            break

        else:
            error("Invalid option. Choose 0–3.")
            pause()
