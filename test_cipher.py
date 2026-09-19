"""
test_cipher.py — Quick self-test for all cipher modules.
Run:  python test_cipher.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# ── Caesar tests ──────────────────────────────────────────────────────────────
from caesar import encrypt as c_enc, decrypt as c_dec, brute_force

assert c_enc("Hello, World!", 3) == "Khoor, Zruog!", "Caesar encrypt failed"
assert c_dec("Khoor, Zruog!", 3) == "Hello, World!", "Caesar decrypt failed"
assert c_dec(c_enc("Python3.11", 13), 13) == "Python3.11",   "Caesar round-trip failed"
print("✔ Caesar cipher — OK")

# ── Vigenère tests ────────────────────────────────────────────────────────────
from vigenere import encrypt as v_enc, decrypt as v_dec

ct = v_enc("AttackAtDawn", "KEY")
assert v_dec(ct, "KEY") == "AttackAtDawn", "Vigenère round-trip failed"
assert v_enc("HELLO", "KEY") == "RIJVS",   "Vigenère encrypt failed"
print("✔ Vigenère cipher — OK")

# ── Frequency analysis tests ──────────────────────────────────────────────────
from frequency_analysis import letter_frequencies, crack_caesar, index_of_coincidence

plain   = "The quick brown fox jumps over the lazy dog"
shifted = c_enc(plain, 7)
results = crack_caesar(shifted)
best_shift = results[0][0]
assert best_shift == 7, f"Frequency analysis cracked wrong shift: {best_shift}"
print("✔ Frequency analysis crack_caesar — OK")

# NOTE: Pangrams have artificially uniform letter distribution (IC ~0.02).
# Use a natural English paragraph so IC reflects true English (~0.065).
ic_text = (
    "To be or not to be that is the question whether tis nobler in the mind "
    "to suffer the slings and arrows of outrageous fortune or to take arms "
    "against a sea of troubles and by opposing end them to die to sleep no more"
)
ic = index_of_coincidence(ic_text)
assert 0.050 <= ic <= 0.080, f"IC out of expected range: {ic:.4f}"
print(f"✔ Index of Coincidence — OK  (IC = {ic:.4f})")

# ── Password tool tests ───────────────────────────────────────────────────────
from password_tool import encrypt_password, decrypt_password, strength_report

pw = "MySecureP@ss99!"

enc_c = encrypt_password(pw, "caesar", 12)
assert decrypt_password(enc_c, "caesar", 12) == pw, "Password Caesar round-trip failed"
print("✔ Password encrypt/decrypt (Caesar) — OK")

enc_v = encrypt_password(pw, "vigenere", "SECURITY")
assert decrypt_password(enc_v, "vigenere", "SECURITY") == pw, "Password Vigenère round-trip failed"
print("✔ Password encrypt/decrypt (Vigenère) — OK")

enc_d = encrypt_password(pw, "double", (7, "CIPHER"))
assert decrypt_password(enc_d, "double", (7, "CIPHER")) == pw, "Password double-layer round-trip failed"
print("✔ Password encrypt/decrypt (Double-layer) — OK")

report = strength_report(pw)
assert report["score"] >= 65,      f"Strong password scored too low: {report['score']}"
assert report["rating"] in ("Strong", "Very Strong"), f"Unexpected rating: {report['rating']}"
print(f"✔ Password strength checker — OK  (score={report['score']}, rating={report['rating']})")

weak_report = strength_report("abc")
assert weak_report["rating"] == "Weak", f"Weak password not rated Weak: {weak_report['rating']}"
print(f"✔ Weak password detection — OK  (score={weak_report['score']})")

# ── Summary ───────────────────────────────────────────────────────────────────
print()
print("=" * 50)
print("  ALL TESTS PASSED ✔")
print("=" * 50)
