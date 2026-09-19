"""
main.py — Caesar & Vigenère Cipher Tool
=========================================
Entry point for the Cipher Tool CLI application.

Features:
  ● Caesar Cipher  — encrypt, decrypt, brute-force all 25 shifts
  ● Vigenère Cipher — encrypt, decrypt with keyword, Kasiski hint
  ● Frequency Analysis — letter charts, auto-crack Caesar/Vigenère, IC calculator
  ● Password Tool  — strength check, encrypt, decrypt, vault save/load

Run:
    python main.py

Requirements:
    pip install colorama      # optional but recommended for color output
"""

import sys
import os

# ── Ensure project directory is on the path ───────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from utils import (banner, section_header, prompt, pause,
                   cyan, yellow, green, dim, red, info, divider)
import caesar
import vigenere
import frequency_analysis
import password_tool


# ── Main menu ─────────────────────────────────────────────────────────────────

def main_menu():
    """Display the main menu and dispatch to sub-modules."""
    while True:
        banner()

        print(f"  {yellow('MAIN MENU')}\n")
        print(f"  {cyan('1.')} 🔡  Caesar Cipher       (encrypt / decrypt / brute-force)")
        print(f"  {cyan('2.')} 🔤  Vigenère Cipher     (encrypt / decrypt / Kasiski)")
        print(f"  {cyan('3.')} 📊  Frequency Analysis  (crack ciphers / letter chart / IC)")
        print(f"  {cyan('4.')} 🔑  Password Tool       (strength check / encrypt / vault)")
        print(f"  {cyan('5.')} ℹ️   About this tool")
        print(f"  {cyan('0.')} 🚪  Exit")
        print()

        choice = prompt("Select an option")

        if choice == "1":
            caesar.menu()

        elif choice == "2":
            vigenere.menu()

        elif choice == "3":
            frequency_analysis.menu()

        elif choice == "4":
            password_tool.menu()

        elif choice == "5":
            _about()

        elif choice == "0":
            banner()
            print(f"  {green('Goodbye! Stay secure. 🔐')}\n")
            sys.exit(0)

        else:
            info("Please enter a number between 0 and 5.")
            pause()


# ── About screen ──────────────────────────────────────────────────────────────

def _about():
    """Display info about the project."""
    section_header("About This Tool")
    print(f"""
  {cyan('Caesar & Vigenère Cipher Tool')}
  {dim('A Python cryptography learning project')}

  {yellow('What this tool demonstrates:')}
    {green('✔')}  Classical cipher algorithm implementation
    {green('✔')}  Frequency analysis for automated cipher breaking
    {green('✔')}  Python tool development from scratch
    {green('✔')}  Understanding of why modern encryption replaced classics
    {green('✔')}  Password strength analysis with entropy measurement
    {green('✔')}  Double-layer cipher encryption for passwords

  {yellow('Ciphers covered:')}
    {cyan('Caesar')}    — monoalphabetic substitution (shift cipher)
    {cyan('Vigenère')} — polyalphabetic substitution (keyword cipher)

  {yellow('Breaking techniques:')}
    {cyan('Brute Force')}          — try all 25 Caesar shifts
    {cyan('Frequency Analysis')}   — match letter distributions to English
    {cyan('Kasiski Examination')}  — estimate Vigenère key length
    {cyan('Index of Coincidence')} — distinguish natural vs. random text

  {yellow('Why classical ciphers were replaced:')}
    {dim('Caesar :')} Only 25 keys → cracked in seconds
    {dim('Vigenère:')} Falls to Kasiski + IC analysis → cracked in hours
    {dim('AES-256 :')} 2^256 key space → centuries to crack with any known attack

  {dim('A working cipher tool with frequency analysis is a great')}
  {dim('conversation starter in any security interview.')}
    """)
    pause()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n  {yellow('Interrupted. Goodbye!')}\n")
        sys.exit(0)
