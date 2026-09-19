"""
password_tool.py — Password Encryption & Management
-----------------------------------------------------
Provides password-specific features:
  • Encrypt a password using Caesar or Vigenère cipher
  • Decrypt a stored encrypted password
  • Check password strength (length, complexity, entropy)
  • Save / load encrypted passwords to a local vault file (JSON)
  • Layer both ciphers together for double-layer encryption

The vault stores passwords in encrypted form only — the tool never writes
plaintext passwords to disk.
"""

import json
import os
import re
import math
from datetime import datetime
from utils import (cyan, yellow, green, red, dim, magenta,
                   result_box, info, error, success, section_header, prompt,
                   prompt_int, pause, divider)
import caesar
import vigenere

# ── Vault file path ───────────────────────────────────────────────────────────
VAULT_FILE = os.path.join(os.path.dirname(__file__), "password_vault.json")


# ── Password Strength Checker ─────────────────────────────────────────────────

def _entropy(password: str) -> float:
    """Shannon entropy in bits per character."""
    if not password:
        return 0.0
    freq = {}
    for c in password:
        freq[c] = freq.get(c, 0) + 1
    n = len(password)
    return -sum((f / n) * math.log2(f / n) for f in freq.values())


def strength_report(password: str) -> dict:
    """
    Analyse a password and return a detailed strength report.

    Returns a dict with:
        score      : 0–100
        rating     : 'Weak' / 'Fair' / 'Strong' / 'Very Strong'
        checks     : dict of individual checks (bool)
        entropy    : Shannon entropy (bits/char)
        suggestions: list of improvement tips
    """
    checks = {
        "length_8":      len(password) >= 8,
        "length_12":     len(password) >= 12,
        "uppercase":     bool(re.search(r'[A-Z]', password)),
        "lowercase":     bool(re.search(r'[a-z]', password)),
        "digits":        bool(re.search(r'\d', password)),
        "symbols":       bool(re.search(r'[^A-Za-z0-9]', password)),
        "no_sequences":  not bool(re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde)', password.lower())),
        "no_repeats":    not bool(re.search(r'(.)\1{2,}', password)),
    }

    score = 0
    score += 10 if checks["length_8"]     else 0
    score += 15 if checks["length_12"]    else 0
    score += 15 if checks["uppercase"]    else 0
    score += 15 if checks["lowercase"]    else 0
    score += 15 if checks["digits"]       else 0
    score += 20 if checks["symbols"]      else 0
    score += 5  if checks["no_sequences"] else 0
    score += 5  if checks["no_repeats"]   else 0

    if score >= 85:
        rating = "Very Strong"
    elif score >= 65:
        rating = "Strong"
    elif score >= 40:
        rating = "Fair"
    else:
        rating = "Weak"

    suggestions = []
    if not checks["length_8"]:   suggestions.append("Use at least 8 characters")
    if not checks["length_12"]:  suggestions.append("Use at least 12 characters for better security")
    if not checks["uppercase"]:  suggestions.append("Add uppercase letters (A–Z)")
    if not checks["lowercase"]:  suggestions.append("Add lowercase letters (a–z)")
    if not checks["digits"]:     suggestions.append("Include numbers (0–9)")
    if not checks["symbols"]:    suggestions.append("Add symbols (!, @, #, $, ...)")
    if not checks["no_sequences"]:suggestions.append("Avoid sequential patterns (123, abc)")
    if not checks["no_repeats"]: suggestions.append("Avoid repeated characters (aaa, 111)")

    return {
        "score":       score,
        "rating":      rating,
        "checks":      checks,
        "entropy":     _entropy(password),
        "suggestions": suggestions,
    }


def print_strength_report(report: dict):
    """Pretty-print a strength report."""
    score  = report["score"]
    rating = report["rating"]

    color_fn = (green if score >= 65 else (yellow if score >= 40 else red))
    bar_w  = int(score / 2)
    bar    = "█" * bar_w + "░" * (50 - bar_w)

    print(f"\n  {color_fn(f'[{bar}]')} {color_fn(f'{score}/100')}")
    print(f"  Rating   : {color_fn(rating)}")
    entropy = report["entropy"]
    print(f"  Entropy  : {dim(f'{entropy:.2f} bits/char')}")
    print()
    print(f"  {yellow('Checks:')}")
    for check, passed in report["checks"].items():
        icon = green("✔") if passed else red("✖")
        label = check.replace("_", " ").title()
        print(f"    {icon}  {label}")

    if report["suggestions"]:
        print(f"\n  {yellow('Tips to improve:')}")
        for tip in report["suggestions"]:
            print(f"    {cyan('→')}  {tip}")


# ── Encryption helpers ────────────────────────────────────────────────────────

def encrypt_password(password: str, method: str, key) -> str:
    """
    Encrypt a password using the chosen method.

    Args:
        password : the plaintext password
        method   : 'caesar', 'vigenere', or 'double'
        key      : int (Caesar shift) or str (Vigenère keyword)
                   For 'double': tuple (shift: int, keyword: str)

    Returns:
        Encrypted password string.
    """
    if method == "caesar":
        return caesar.encrypt(password, int(key))
    elif method == "vigenere":
        return vigenere.encrypt(password, str(key))
    elif method == "double":
        shift, keyword = key
        step1 = caesar.encrypt(password, int(shift))
        return vigenere.encrypt(step1, str(keyword))
    else:
        raise ValueError(f"Unknown method: {method}")


def decrypt_password(encrypted: str, method: str, key) -> str:
    """
    Decrypt an encrypted password.

    Args:
        encrypted : the encrypted password string
        method    : 'caesar', 'vigenere', or 'double'
        key       : matching key used during encryption
                    For 'double': tuple (shift: int, keyword: str)

    Returns:
        Original plaintext password.
    """
    if method == "caesar":
        return caesar.decrypt(encrypted, int(key))
    elif method == "vigenere":
        return vigenere.decrypt(encrypted, str(key))
    elif method == "double":
        shift, keyword = key
        step1 = vigenere.decrypt(encrypted, str(keyword))
        return caesar.decrypt(step1, int(shift))
    else:
        raise ValueError(f"Unknown method: {method}")


# ── Vault ─────────────────────────────────────────────────────────────────────

def _load_vault() -> dict:
    if os.path.exists(VAULT_FILE):
        with open(VAULT_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_vault(vault: dict):
    with open(VAULT_FILE, "w") as f:
        json.dump(vault, f, indent=2)


def vault_add(label: str, encrypted: str, method: str, hint: str = ""):
    """Add an encrypted password entry to the vault."""
    vault = _load_vault()
    vault[label] = {
        "encrypted": encrypted,
        "method":    method,
        "hint":      hint,
        "saved_at":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    _save_vault(vault)


def vault_list() -> dict:
    """Return all vault entries."""
    return _load_vault()


def vault_delete(label: str) -> bool:
    vault = _load_vault()
    if label in vault:
        del vault[label]
        _save_vault(vault)
        return True
    return False


# ── Interactive menu handler ──────────────────────────────────────────────────

def _pick_method():
    """Ask user to pick an encryption method. Returns (method, key)."""
    print(f"\n  {yellow('Encryption method:')}")
    print(f"  {cyan('1.')} Caesar cipher (shift number)")
    print(f"  {cyan('2.')} Vigenère cipher (keyword)")
    print(f"  {cyan('3.')} Double-layer (Caesar → Vigenère)")
    choice = prompt("Select method")

    if choice == "1":
        shift = prompt_int("Enter shift (1-25)", 1, 25)
        return "caesar", shift

    elif choice == "2":
        keyword = prompt("Enter Vigenère keyword (letters only)")
        return "vigenere", keyword

    elif choice == "3":
        shift   = prompt_int("Enter Caesar shift (1-25)", 1, 25)
        keyword = prompt("Enter Vigenère keyword")
        return "double", (shift, keyword)

    else:
        error("Invalid method selected.")
        return None, None


def menu():
    """Interactive sub-menu for password encryption & management."""
    while True:
        section_header("Password Encryption & Vault")
        print(f"  {cyan('1.')} Check password strength")
        print(f"  {cyan('2.')} Encrypt a password")
        print(f"  {cyan('3.')} Decrypt a password")
        print(f"  {cyan('4.')} Save encrypted password to vault")
        print(f"  {cyan('5.')} View vault")
        print(f"  {cyan('6.')} Delete vault entry")
        print(f"  {cyan('0.')} Back to main menu")

        choice = prompt("Select option")

        # ── Strength check ────────────────────────────────────────────────────
        if choice == "1":
            pw = prompt("Enter password to check (input is visible)")
            report = strength_report(pw)
            print_strength_report(report)
            pause()

        # ── Encrypt ───────────────────────────────────────────────────────────
        elif choice == "2":
            pw = prompt("Enter password to encrypt")
            method, key = _pick_method()
            if method:
                try:
                    enc = encrypt_password(pw, method, key)
                    result_box("Encrypted password:", enc)
                    info("Save your key/keyword to decrypt later!")
                except ValueError as e:
                    error(str(e))
            pause()

        # ── Decrypt ───────────────────────────────────────────────────────────
        elif choice == "3":
            enc    = prompt("Enter encrypted password")
            method, key = _pick_method()
            if method:
                try:
                    plain = decrypt_password(enc, method, key)
                    result_box("Original password:", plain)
                except ValueError as e:
                    error(str(e))
            pause()

        # ── Save to vault ─────────────────────────────────────────────────────
        elif choice == "4":
            pw     = prompt("Enter password to encrypt and save")
            label  = prompt("Enter a label for this entry (e.g. 'Gmail')")
            method, key = _pick_method()
            if method:
                try:
                    enc  = encrypt_password(pw, method, key)
                    hint = prompt("Optional key hint (leave blank to skip)")
                    vault_add(label, enc, method, hint)
                    result_box("Saved to vault:", enc)
                    success(f"Entry '{label}' saved to vault.")
                    info("Remember your key — it is NOT stored in the vault!")
                except ValueError as e:
                    error(str(e))
            pause()

        # ── View vault ────────────────────────────────────────────────────────
        elif choice == "5":
            vault = vault_list()
            if not vault:
                info("Vault is empty.")
            else:
                print(f"\n  {yellow('Stored encrypted passwords:')}\n")
                for label, entry in vault.items():
                    print(f"  {cyan(label)}")
                    print(f"    Encrypted : {green(entry['encrypted'])}")
                    print(f"    Method    : {dim(entry['method'])}")
                    print(f"    Hint      : {dim(entry.get('hint', 'none'))}")
                    print(f"    Saved at  : {dim(entry.get('saved_at', ''))}")
                    print()
            pause()

        # ── Delete ────────────────────────────────────────────────────────────
        elif choice == "6":
            vault = vault_list()
            if not vault:
                info("Vault is empty.")
            else:
                print(f"\n  {yellow('Current entries:')}")
                for label in vault:
                    print(f"    {cyan('•')} {label}")
                label = prompt("Enter label to delete")
                if vault_delete(label):
                    success(f"Entry '{label}' deleted.")
                else:
                    error(f"Label '{label}' not found.")
            pause()

        elif choice == "0":
            break

        else:
            error("Invalid option. Choose 0–6.")
            pause()
