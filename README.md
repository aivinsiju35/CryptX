# 🔐 Caesar & Vigenère Cipher Tool

A Python cryptography project that **encrypts**, **decrypts**, and **breaks** classical ciphers — with a built-in **password encryption vault**.

---

## 📁 Project Structure

```
cipher_tool/
├── main.py                # CLI entry point — run this
├── caesar.py              # Caesar cipher (encrypt / decrypt / brute-force)
├── vigenere.py            # Vigenère cipher (encrypt / decrypt / Kasiski)
├── frequency_analysis.py  # Cipher breaking + letter frequency charts
├── password_tool.py       # Password strength + encrypt/decrypt + vault
├── utils.py               # Colored terminal UI helpers
├── password_vault.json    # Created automatically when vault is used
├── test_cipher.py         # Self-test script (run to verify everything works)
└── requirements.txt       # External dependencies
```

---

## ⚡ Quick Start

```bash
# 1. Install the optional color library
pip install colorama

# 2. Run the tool
python main.py

# 3. Run tests to verify everything works
python test_cipher.py
```

---

## 🎯 Features

### 🔡 Caesar Cipher
- Encrypt any text with a shift (1–25)
- Decrypt with the known shift
- **Brute-force**: see all 25 possible decryptions at once

### 🔤 Vigenère Cipher
- Encrypt / decrypt with any keyword (letters only)
- **Kasiski Examination**: estimates the likely keyword length from repeated patterns — a first step toward cracking it

### 📊 Frequency Analysis
| Feature | Description |
|---------|-------------|
| Letter Frequency Chart | ASCII bar chart comparing your text against English |
| Auto-crack Caesar | Chi-squared scoring ranks all 25 shifts by English likeness |
| Crack Vigenère | Given a key length, recovers the keyword using column frequency analysis |
| Index of Coincidence | Measures how "English-like" a text is (IC ≈ 0.065 = English) |

### 🔑 Password Tool
| Feature | Description |
|---------|-------------|
| Strength Checker | Score 0–100, rating, entropy, 8 checks, improvement tips |
| Caesar Encrypt | Encrypt password with a shift number |
| Vigenère Encrypt | Encrypt password with a keyword |
| **Double-Layer** | Caesar → Vigenère for stronger password protection |
| Vault | Save encrypted passwords to `password_vault.json` (keys NOT stored) |

---

## 💡 How Each Cipher Works

### Caesar Cipher
Every letter is shifted forward in the alphabet by a fixed number.

```
Plaintext : H  E  L  L  O
Shift     : 3  3  3  3  3
Ciphertext: K  H  O  O  R
```

**Breaking it**: Only 25 possible keys. Brute-force all of them in milliseconds.

---

### Vigenère Cipher
Each letter uses a *different* shift based on a repeating keyword.

```
Plaintext : A  T  T  A  C  K  A  T  D  A  W  N
Keyword   : K  E  Y  K  E  Y  K  E  Y  K  E  Y
Shifts    : 10 4  24 10 4  24 10 4  24 10 4  24
Ciphertext: K  X  R  K  G  I  K  X  B  K  A  L
```

**Breaking it**: Use the Kasiski test to find key length, then frequency-analyze each column as an independent Caesar cipher.

---

## 🔬 Why Modern Encryption Replaced These

| Cipher | Key Space | Time to Crack |
|--------|-----------|---------------|
| Caesar | 25 | < 1 second |
| Vigenère | Millions | Hours–Days |
| AES-256 | 2^256 | Centuries |

Classical ciphers fail because they preserve the **statistical structure** of natural language. Modern ciphers produce output that is statistically indistinguishable from random data.

---

## 🧪 Running Tests

```bash
python test_cipher.py
```

Tests cover:
- Caesar encrypt/decrypt round-trips
- Vigenère encrypt/decrypt round-trips
- Frequency analysis correctly identifying the shift
- Index of Coincidence within expected English range
- Password encryption (Caesar, Vigenère, double-layer) round-trips
- Password strength scoring

---

## 📚 Skills Demonstrated

- ✔ Classical cipher algorithm implementation
- ✔ Frequency analysis for automated cipher breaking
- ✔ Python modular tool development from scratch
- ✔ Security mindset: building attacks, not just defenses
- ✔ Password strength metrics (entropy, complexity scoring)
- ✔ File-backed encrypted data storage

> *A working cipher tool with frequency analysis is a great conversation starter in any security interview.*
