"""
app.py — CryptX GUI Application
=================================
Modern desktop app with full Light / Dark mode switching.

Run:
    pip install customtkinter
    python app.py

Build standalone .exe:
    python -m PyInstaller --onefile --windowed --name CryptX app.py
"""

import os, sys, tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

sys.path.insert(0, os.path.dirname(__file__))
import caesar, vigenere, frequency_analysis, password_tool

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Colour palettes ────────────────────────────────────────────────────────────
DARK = {
    "bg":          "#0d1117",
    "sidebar":     "#161b22",
    "card":        "#161b22",
    "divider":     "#30363d",
    "input_bg":    "#0d1117",
    "input_text":  "#e6edf3",
    "result_text": "#3fb950",
    "border":      "#30363d",
    "subtext":     "#8b949e",
    "heading":     "#e6edf3",
    "accent":      "#58a6ff",
    "nav_hover":   "#21262d",
    "detail_text": "#c9d1d9",
    "chart_eng":   "#21262d",
    "chart_bar":   "#58a6ff",
    "chart_low":   "#f85149",
    "chart_lbl":   "#8b949e",
}
LIGHT = {
    "bg":          "#f6f8fa",
    "sidebar":     "#ffffff",
    "card":        "#ffffff",
    "divider":     "#d0d7de",
    "input_bg":    "#ffffff",
    "input_text":  "#1f2328",
    "result_text": "#1a7f37",
    "border":      "#d0d7de",
    "subtext":     "#57606a",
    "heading":     "#1f2328",
    "accent":      "#0969da",
    "nav_hover":   "#eaeef2",
    "detail_text": "#1f2328",
    "chart_eng":   "#d0d7de",
    "chart_bar":   "#0969da",
    "chart_low":   "#cf222e",
    "chart_lbl":   "#57606a",
}

_pal: dict = DARK   # active palette

def P() -> dict:
    return _pal

NAV_ITEMS = [
    ("🔡  Caesar Cipher",      "caesar"),
    ("🔤  Vigenère Cipher",    "vigenere"),
    ("📊  Frequency Analysis", "frequency"),
    ("🔑  Password Tool",      "password"),
    ("ℹ️   About",              "about"),
]


# ═══════════════════════════════════════════════════════════════════════════════
#  Shared widget factories
# ═══════════════════════════════════════════════════════════════════════════════

def make_card(parent) -> ctk.CTkFrame:
    return ctk.CTkFrame(parent, corner_radius=12, fg_color=P()["card"])

def primary_btn(parent, text, cmd, color="#1f6feb", hover="#388bfd", **kw) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent, text=text, command=cmd, height=36, corner_radius=8,
        font=ctk.CTkFont(size=13, weight="bold"),
        fg_color=color, hover_color=hover, **kw)

def set_result(tb: ctk.CTkTextbox, text: str):
    tb.configure(state="normal")
    tb.delete("1.0", "end")
    tb.insert("1.0", text)
    tb.configure(state="disabled")


# ═══════════════════════════════════════════════════════════════════════════════
#  BasePanel — theme registration system
# ═══════════════════════════════════════════════════════════════════════════════

class BasePanel(ctk.CTkScrollableFrame):
    """
    All panels inherit from this. Each widget is registered with a lambda
    that describes how to update it when the palette changes.
    apply_theme(p) runs all registered lambdas with the new palette.
    """
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=P()["bg"], corner_radius=0, **kw)
        self._fns: list = []   # list of callables: fn(palette_dict)

    # ── Registration helpers ──────────────────────────────────────────────────

    def _reg(self, widget, fn):
        """Register (widget, update-fn). fn receives the new palette dict."""
        self._fns.append(lambda p, w=widget, f=fn: f(w, p))
        return widget

    def _reg_panel(self, w):
        return self._reg(w, lambda w, p: w.configure(fg_color=p["bg"]))

    def _reg_card(self, w):
        return self._reg(w, lambda w, p: w.configure(fg_color=p["card"]))

    def _reg_input(self, w):
        return self._reg(w, lambda w, p: w.configure(
            fg_color=p["input_bg"], text_color=p["input_text"], border_color=p["border"]))

    def _reg_output(self, w):
        return self._reg(w, lambda w, p: w.configure(
            fg_color=p["input_bg"], text_color=p["result_text"], border_color=p["border"]))

    def _reg_detail(self, w):
        return self._reg(w, lambda w, p: w.configure(
            fg_color=p["card"], text_color=p["detail_text"], border_color=p["border"]))

    def _reg_entry(self, w):
        return self._reg(w, lambda w, p: w.configure(
            fg_color=p["input_bg"], text_color=p["input_text"], border_color=p["border"]))

    def _reg_heading(self, w):
        return self._reg(w, lambda w, p: w.configure(text_color=p["heading"]))

    def _reg_subtext(self, w):
        return self._reg(w, lambda w, p: w.configure(text_color=p["subtext"]))

    def _reg_accent(self, w):
        return self._reg(w, lambda w, p: w.configure(text_color=p["accent"]))

    def _reg_canvas(self, w):
        return self._reg(w, lambda w, p: w.configure(bg=p["bg"]))

    # ── Helpers for creating and auto-registering common widgets ──────────────

    def _heading(self, text: str) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(self, text=text,
                           font=ctk.CTkFont(size=22, weight="bold"),
                           text_color=P()["heading"])
        lbl.pack(anchor="w", padx=24, pady=(24, 2))
        return self._reg_heading(lbl)

    def _subtitle(self, text: str) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(self, text=text,
                           font=ctk.CTkFont(size=12), text_color=P()["subtext"])
        lbl.pack(anchor="w", padx=24, pady=(0, 16))
        return self._reg_subtext(lbl)

    def _section_label(self, parent, text: str) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(parent, text=text,
                           font=ctk.CTkFont(size=13, weight="bold"),
                           text_color=P()["accent"])
        lbl.pack(anchor="w", padx=16, pady=(14, 4))
        return self._reg_accent(lbl)

    def _inline_label(self, parent, text: str, color_key="subtext") -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(parent, text=text,
                           font=ctk.CTkFont(size=12), text_color=P()[color_key])
        return self._reg(lbl, lambda w, p, k=color_key: w.configure(text_color=p[k]))

    def _text_input(self, parent, height=110, placeholder="") -> ctk.CTkTextbox:
        p = P()
        tb = ctk.CTkTextbox(parent, height=height,
                            font=ctk.CTkFont(family="Consolas", size=13),
                            fg_color=p["input_bg"], text_color=p["input_text"],
                            border_color=p["border"], border_width=1, corner_radius=8)
        tb.pack(fill="x", padx=16, pady=(0, 12))
        if placeholder:
            tb.insert("1.0", placeholder)
            tb.configure(text_color=p["subtext"])
            def _clear(e, tb=tb):
                if tb.get("1.0", "end").strip() == placeholder:
                    tb.delete("1.0", "end")
                    tb.configure(text_color=P()["input_text"])
            tb.bind("<FocusIn>", _clear)
        return self._reg_input(tb)

    def _result_box(self, parent, height=130) -> ctk.CTkTextbox:
        p = P()
        tb = ctk.CTkTextbox(parent, height=height,
                            font=ctk.CTkFont(family="Consolas", size=13),
                            fg_color=p["input_bg"], text_color=p["result_text"],
                            border_color=p["border"], border_width=1, corner_radius=8)
        tb.pack(fill="x", padx=16, pady=(4, 14))
        tb.configure(state="disabled")
        return self._reg_output(tb)

    def _entry(self, parent, **kw) -> ctk.CTkEntry:
        p = P()
        e = ctk.CTkEntry(parent, fg_color=p["input_bg"],
                         border_color=p["border"], border_width=1, **kw)
        return self._reg_entry(e)

    # ── Apply theme to all registered widgets ─────────────────────────────────

    def apply_theme(self, p: dict):
        self.configure(fg_color=p["bg"])
        for fn in self._fns:
            try:
                fn(p)
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════════════════════
#  Main Application Window
# ═══════════════════════════════════════════════════════════════════════════════

class CipherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🔐  CryptX — Cipher & Password Tool")
        self.geometry("1160x740")
        self.minsize(960, 640)
        self.configure(fg_color=P()["bg"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._panels:   dict[str, BasePanel]     = {}
        self._nav_btns: dict[str, ctk.CTkButton] = {}
        self._active:   str | None = None

        self._build_sidebar()
        self._build_panels()
        self.show_panel("caesar")

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        p = P()
        self._sb = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=p["sidebar"])
        self._sb.grid(row=0, column=0, sticky="nsew")
        self._sb.grid_propagate(False)
        self._sb.grid_rowconfigure(len(NAV_ITEMS) + 3, weight=1)

        # Logo
        self._logo_lbl = ctk.CTkLabel(self._sb, text="🔐  CryptX",
                                      font=ctk.CTkFont(size=21, weight="bold"),
                                      text_color=p["accent"])
        self._logo_lbl.grid(row=0, column=0, padx=20, pady=(28, 2), sticky="w")

        self._sub_lbl = ctk.CTkLabel(self._sb, text="Classical Cryptography Suite",
                                     font=ctk.CTkFont(size=11), text_color=p["subtext"])
        self._sub_lbl.grid(row=1, column=0, padx=20, pady=(0, 18), sticky="w")

        self._div1 = ctk.CTkFrame(self._sb, height=1, fg_color=p["divider"])
        self._div1.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))

        for i, (label, key) in enumerate(NAV_ITEMS, start=3):
            btn = ctk.CTkButton(
                self._sb, text=label, anchor="w", corner_radius=8, height=44,
                font=ctk.CTkFont(size=13), fg_color="transparent",
                hover_color=p["nav_hover"], text_color=p["detail_text"],
                command=lambda k=key: self.show_panel(k))
            btn.grid(row=i, column=0, padx=12, pady=2, sticky="ew")
            self._nav_btns[key] = btn

        ctk.CTkLabel(self._sb, text="", fg_color="transparent").grid(
            row=len(NAV_ITEMS) + 3, column=0, sticky="nsew")

        self._div2 = ctk.CTkFrame(self._sb, height=1, fg_color=p["divider"])
        self._div2.grid(row=len(NAV_ITEMS) + 4, column=0, sticky="ew", padx=16)

        self._mode_switch = ctk.CTkSwitch(self._sb, text="Light Mode",
                                          command=self._toggle_theme,
                                          font=ctk.CTkFont(size=12),
                                          text_color=p["subtext"])
        self._mode_switch.grid(row=len(NAV_ITEMS) + 5, column=0,
                               padx=20, pady=16, sticky="sw")

    # ── Theme toggle ──────────────────────────────────────────────────────────

    def _toggle_theme(self):
        global _pal
        is_dark = ctk.get_appearance_mode() == "Dark"
        ctk.set_appearance_mode("light" if is_dark else "dark")
        _pal = LIGHT if is_dark else DARK
        p = _pal

        # Window + sidebar
        self.configure(fg_color=p["bg"])
        self._sb.configure(fg_color=p["sidebar"])
        self._logo_lbl.configure(text_color=p["accent"])
        self._sub_lbl.configure(text_color=p["subtext"])
        self._div1.configure(fg_color=p["divider"])
        self._div2.configure(fg_color=p["divider"])
        self._mode_switch.configure(text_color=p["subtext"])

        # Nav buttons
        for key, btn in self._nav_btns.items():
            if key == self._active:
                btn.configure(fg_color="#1f6feb", text_color="white",
                              hover_color="#388bfd")
            else:
                btn.configure(fg_color="transparent", text_color=p["detail_text"],
                              hover_color=p["nav_hover"])

        # All panels
        for panel in self._panels.values():
            panel.apply_theme(p)

    def show_panel(self, key: str):
        p = P()
        if self._active:
            self._panels[self._active].grid_remove()
            self._nav_btns[self._active].configure(
                fg_color="transparent", text_color=p["detail_text"],
                hover_color=p["nav_hover"])
        self._panels[key].grid(row=0, column=1, sticky="nsew")
        self._nav_btns[key].configure(fg_color="#1f6feb", text_color="white",
                                      hover_color="#388bfd")
        self._active = key

    def _build_panels(self):
        for key, cls in [("caesar",    CaesarPanel),
                         ("vigenere",  VigenerePanel),
                         ("frequency", FrequencyPanel),
                         ("password",  PasswordPanel),
                         ("about",     AboutPanel)]:
            self._panels[key] = cls(self)
            self._panels[key].grid(row=0, column=1, sticky="nsew")
            self._panels[key].grid_remove()


# ═══════════════════════════════════════════════════════════════════════════════
#  Panel 1 — Caesar Cipher
# ═══════════════════════════════════════════════════════════════════════════════

class CaesarPanel(BasePanel):
    def __init__(self, master):
        super().__init__(master)
        self._build()

    def _build(self):
        p = P()
        self._heading("🔡  Caesar Cipher")
        self._subtitle("Shifts every letter by a fixed number (1–25).  Non-letter characters are preserved.")

        # ── Input card ────────────────────────────────────────────────────────
        card = self._reg_card(make_card(self))
        card.pack(fill="x", padx=20, pady=6)

        self._section_label(card, "Input Text")
        self.cipher_input = self._text_input(card, 110, "Type or paste text here…")

        self._section_label(card, "Shift Value")
        sr = ctk.CTkFrame(card, fg_color="transparent")
        sr.pack(fill="x", padx=16, pady=(0, 14))

        self.shift_var = tk.IntVar(value=3)
        self.shift_disp = ctk.CTkLabel(sr, text="3", width=40,
                                       font=ctk.CTkFont(size=22, weight="bold"),
                                       text_color=p["accent"])
        self.shift_disp.pack(side="left")
        self._reg_accent(self.shift_disp)

        ctk.CTkSlider(sr, from_=1, to=25, variable=self.shift_var,
                      number_of_steps=24, width=320,
                      command=lambda v: self.shift_disp.configure(text=str(int(v)))
                      ).pack(side="left", padx=14)

        range_lbl = self._inline_label(sr, "(1 – 25)")
        range_lbl.pack(side="left")

        # Buttons
        br = ctk.CTkFrame(card, fg_color="transparent")
        br.pack(fill="x", padx=16, pady=(0, 16))
        primary_btn(br, "🔒  Encrypt",            self._encrypt).pack(side="left", padx=(0, 8))
        primary_btn(br, "🔓  Decrypt",            self._decrypt, "#238636", "#2ea043").pack(side="left", padx=(0, 8))
        primary_btn(br, "⚡  Brute-Force All 25", self._brute,   "#6e40c9", "#8957e5").pack(side="left")

        # ── Result card ───────────────────────────────────────────────────────
        out = self._reg_card(make_card(self))
        out.pack(fill="x", padx=20, pady=6)
        self._section_label(out, "Result")
        self.cipher_output = self._result_box(out, 160)

    def _text(self):
        t = self.cipher_input.get("1.0", "end").strip()
        if not t:
            messagebox.showwarning("Input needed", "Enter some text first.")
        return t

    def _encrypt(self):
        t = self._text()
        if t:
            s = self.shift_var.get()
            set_result(self.cipher_output, f"[Encrypted | Shift = {s}]\n\n{caesar.encrypt(t, s)}")

    def _decrypt(self):
        t = self._text()
        if t:
            s = self.shift_var.get()
            set_result(self.cipher_output, f"[Decrypted | Shift = {s}]\n\n{caesar.decrypt(t, s)}")

    def _brute(self):
        t = self._text()
        if t:
            lines = ["[Brute-Force — All 25 Shifts]\n"]
            for sh, pl in caesar.brute_force(t).items():
                lines.append(f"  Shift {sh:>2}:  {pl}")
            set_result(self.cipher_output, "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════════
#  Panel 2 — Vigenère Cipher
# ═══════════════════════════════════════════════════════════════════════════════

class VigenerePanel(BasePanel):
    def __init__(self, master):
        super().__init__(master)
        self._build()

    def _build(self):
        self._heading("🔤  Vigenère Cipher")
        self._subtitle("Polyalphabetic cipher — each letter gets a different Caesar shift driven by a keyword.")

        card = self._reg_card(make_card(self))
        card.pack(fill="x", padx=20, pady=6)

        self._section_label(card, "Input Text")
        self.vig_input = self._text_input(card, 110, "Type or paste text here…")

        self._section_label(card, "Keyword  (letters only — case insensitive)")
        self.key_entry = self._entry(card, height=40,
                                     font=ctk.CTkFont(family="Consolas", size=14),
                                     placeholder_text="e.g.  SECRET", corner_radius=8)
        self.key_entry.pack(fill="x", padx=16, pady=(0, 14))

        br = ctk.CTkFrame(card, fg_color="transparent")
        br.pack(fill="x", padx=16, pady=(0, 16))
        primary_btn(br, "🔒  Encrypt",                self._encrypt).pack(side="left", padx=(0, 8))
        primary_btn(br, "🔓  Decrypt",                self._decrypt, "#238636", "#2ea043").pack(side="left", padx=(0, 8))
        primary_btn(br, "🔍  Kasiski Key-Length Hint", self._kasiski, "#b45309", "#d4a72c").pack(side="left")

        out = self._reg_card(make_card(self))
        out.pack(fill="x", padx=20, pady=6)
        self._section_label(out, "Result")
        self.vig_output = self._result_box(out, 160)

    def _get_inputs(self):
        t = self.vig_input.get("1.0", "end").strip()
        k = self.key_entry.get().strip()
        if not t or not k:
            messagebox.showwarning("Input needed", "Enter text AND a keyword.")
            return None, None
        return t, k

    def _encrypt(self):
        t, k = self._get_inputs()
        if t:
            try:
                set_result(self.vig_output, f"[Encrypted | Key = {k.upper()}]\n\n{vigenere.encrypt(t, k)}")
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def _decrypt(self):
        t, k = self._get_inputs()
        if t:
            try:
                set_result(self.vig_output, f"[Decrypted | Key = {k.upper()}]\n\n{vigenere.decrypt(t, k)}")
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def _kasiski(self):
        t = self.vig_input.get("1.0", "end").strip()
        if not t:
            messagebox.showwarning("Input needed", "Enter some ciphertext first.")
            return
        hints = vigenere.kasiski_key_length_hint(t)
        if hints:
            lines = ["[Kasiski Examination — Probable Key Lengths]\n"]
            for i, kl in enumerate(hints, 1):
                lines.append(f"    #{i}   Key length ≈ {kl}")
            lines.append("\nUse Frequency Analysis → Crack Vigenère with one of these lengths.")
        else:
            lines = ["Not enough repeated patterns found.",
                     "Try with a longer ciphertext (100+ letters)."]
        set_result(self.vig_output, "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════════
#  Panel 3 — Frequency Analysis
# ═══════════════════════════════════════════════════════════════════════════════

class FrequencyPanel(BasePanel):
    def __init__(self, master):
        super().__init__(master)
        self._freq_data: dict = {}
        self._build()

    def _build(self):
        p = P()
        self._heading("📊  Frequency Analysis")
        self._subtitle("Exploit English letter statistics to automatically break classical ciphers.")

        card = self._reg_card(make_card(self))
        card.pack(fill="x", padx=20, pady=6)

        self._section_label(card, "Ciphertext Input")
        self.freq_input = self._text_input(card, 110, "Paste ciphertext here to analyse or crack…")

        br1 = ctk.CTkFrame(card, fg_color="transparent")
        br1.pack(fill="x", padx=16, pady=(0, 6))
        primary_btn(br1, "🎯  Auto-Crack Caesar",    self._crack_caesar).pack(side="left", padx=(0, 8))
        primary_btn(br1, "📏  Index of Coincidence", self._ic,           "#6e40c9", "#8957e5").pack(side="left", padx=(0, 8))
        primary_btn(br1, "📊  Frequency Table",      self._freq_table,   "#0969da", "#1158c7").pack(side="left")

        br2 = ctk.CTkFrame(card, fg_color="transparent")
        br2.pack(fill="x", padx=16, pady=(0, 14))
        kl_lbl = self._inline_label(br2, "Crack Vigenère — key length:")
        kl_lbl.pack(side="left")

        self.kl_var = tk.IntVar(value=4)
        kl_entry = self._entry(br2, textvariable=self.kl_var, width=55, height=32,
                               font=ctk.CTkFont(size=13))
        kl_entry.pack(side="left", padx=8)
        primary_btn(br2, "🔓  Crack Vigenère", self._crack_vigenere, "#238636", "#2ea043").pack(side="left")

        out = self._reg_card(make_card(self))
        out.pack(fill="x", padx=20, pady=6)
        self._section_label(out, "Analysis Result")
        self.freq_output = self._result_box(out, 190)

        # ── Bar chart card ────────────────────────────────────────────────────
        chart_card = self._reg_card(make_card(self))
        chart_card.pack(fill="x", padx=20, pady=(6, 20))
        self._section_label(chart_card, "Letter Frequency Bar Chart")
        chart_hint = self._inline_label(
            chart_card, "  🔵 Your text   ░ English average  (run any action above to update)")
        chart_hint.pack(anchor="w", padx=16)

        self.canvas = self._reg_canvas(
            tk.Canvas(chart_card, height=210, bg=p["bg"], highlightthickness=0))
        self.canvas.pack(fill="x", padx=16, pady=(4, 16))
        self.canvas.bind("<Configure>", lambda e: self._redraw_chart())

    # ── Override apply_theme to also redraw chart ─────────────────────────────
    def apply_theme(self, p: dict):
        super().apply_theme(p)
        self._redraw_chart()   # redraw bars with new palette colours

    def _text(self):
        t = self.freq_input.get("1.0", "end").strip()
        if not t:
            messagebox.showwarning("Input needed", "Enter some text to analyse.")
        return t

    def _crack_caesar(self):
        t = self._text()
        if not t:
            return
        results = frequency_analysis.crack_caesar(t)
        lines = ["[Auto-Crack Caesar — Ranked by English Likelihood]\n"]
        for rank, (shift, score, plain) in enumerate(results[:8], 1):
            star = "★ BEST " if rank == 1 else f"  #{rank}   "
            lines.append(f"  {star}  Shift {shift:>2}  →  {plain}")
        lines.append(f"\n  Most likely shift: {results[0][0]}")
        set_result(self.freq_output, "\n".join(lines))
        self._update_chart(t)

    def _crack_vigenere(self):
        t = self._text()
        if not t:
            return
        try:
            kl = int(self.kl_var.get())
        except Exception:
            messagebox.showerror("Error", "Enter a valid integer key length.")
            return
        key, plain = frequency_analysis.crack_vigenere(t, kl)
        set_result(self.freq_output,
                   f"[Crack Vigenère | Key Length = {kl}]\n\n"
                   f"  Guessed Key : {key}\n\n"
                   f"  Decrypted   :\n  {plain}")

    def _ic(self):
        t = self._text()
        if not t:
            return
        ic = frequency_analysis.index_of_coincidence(t)
        verdict = (
            "English plaintext / Caesar  (IC ≈ 0.065)"    if ic >= 0.060 else
            "Vigenère with short key     (IC 0.045–0.060)" if ic >= 0.045 else
            "Random / long-key Vigenère  (IC ≈ 0.038)"
        )
        set_result(self.freq_output,
                   f"[Index of Coincidence]\n\n  IC = {ic:.4f}\n\n"
                   f"  Verdict : {verdict}\n\n"
                   f"  Reference:\n"
                   f"    English text      ≈ 0.065\n"
                   f"    Vigenère cipher   ≈ 0.038 – 0.055\n"
                   f"    Pure random text  ≈ 0.038")
        self._update_chart(t)

    def _freq_table(self):
        t = self._text()
        if not t:
            return
        freq = frequency_analysis.letter_frequencies(t)
        lines = ["[Letter Frequency Table]\n",
                 f"  {'Letter':<8} {'Your Text':>10}   {'English Avg':>11}   Diff"]
        lines.append("  " + "─" * 44)
        for letter in "ETAOINSHRDLCUMWFGYPBVKJXQZ":
            pct  = freq[letter]
            eng  = frequency_analysis.ENGLISH_FREQ.get(letter, 0)
            diff = pct - eng
            arrow = "↑" if diff > 1 else ("↓" if diff < -1 else "≈")
            lines.append(f"  {letter:<8} {pct:>9.2f}%   {eng:>9.2f}%   {arrow} {abs(diff):.2f}")
        set_result(self.freq_output, "\n".join(lines))
        self._update_chart(t)

    def _update_chart(self, text: str):
        self._freq_data = frequency_analysis.letter_frequencies(text)
        self._redraw_chart()

    def _redraw_chart(self):
        if not self._freq_data:
            return
        c  = self.canvas
        p  = P()
        c.delete("all")
        c.configure(bg=p["bg"])

        w       = c.winfo_width() or 820
        letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        n       = len(letters)
        slot_w  = (w - 40) // n
        bar_w   = max(4, slot_w - 4)
        bottom  = 195

        for i, letter in enumerate(letters):
            x   = 20 + i * slot_w
            pct = self._freq_data.get(letter, 0)
            eng = frequency_analysis.ENGLISH_FREQ.get(letter, 0)

            # English average bar (background)
            eh = min(int(eng * 160 / 15), 160)
            c.create_rectangle(x, bottom - eh, x + bar_w, bottom,
                               fill=p["chart_eng"], outline="")

            # Text frequency bar
            th = min(int(pct * 160 / 15), 160)
            if pct > 0:
                color = p["chart_bar"] if pct >= eng - 1.5 else p["chart_low"]
                c.create_rectangle(x + 1, bottom - th, x + bar_w - 1, bottom,
                                   fill=color, outline="")
                c.create_text(x + bar_w // 2, bottom - th - 8,
                              text=f"{pct:.0f}", fill=p["chart_lbl"],
                              font=("Consolas", 7))

            c.create_text(x + bar_w // 2, bottom + 12,
                          text=letter, fill=p["chart_lbl"],
                          font=("Consolas", 9, "bold"))


# ═══════════════════════════════════════════════════════════════════════════════
#  Panel 4 — Password Tool
# ═══════════════════════════════════════════════════════════════════════════════

class PasswordPanel(BasePanel):
    def __init__(self, master):
        super().__init__(master)
        self._last_encrypted = ""
        self._build()

    def _build(self):
        p = P()
        self._heading("🔑  Password Encryption Tool")
        self._subtitle("Analyse password strength, encrypt with classical ciphers, and manage a local encrypted vault.")

        # ── Strength checker card ─────────────────────────────────────────────
        sc = self._reg_card(make_card(self))
        sc.pack(fill="x", padx=20, pady=6)
        self._section_label(sc, "Password Strength Checker")

        pr = ctk.CTkFrame(sc, fg_color="transparent")
        pr.pack(fill="x", padx=16, pady=(0, 8))

        self.pw_entry = self._entry(pr, height=40,
                                    font=ctk.CTkFont(family="Consolas", size=14),
                                    placeholder_text="Enter password here…",
                                    corner_radius=8, show="●")
        self.pw_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self._show_var = ctk.BooleanVar()
        show_cb = ctk.CTkCheckBox(pr, text="Show", variable=self._show_var,
                                  command=lambda: self.pw_entry.configure(
                                      show="" if self._show_var.get() else "●"),
                                  font=ctk.CTkFont(size=12), text_color=p["subtext"])
        show_cb.pack(side="left")
        self._reg_subtext(show_cb)

        primary_btn(sc, "🔬  Analyse Strength", self._check_strength
                    ).pack(anchor="w", padx=16, pady=(0, 10))

        self.str_bar = ctk.CTkProgressBar(sc, height=16, corner_radius=8)
        self.str_bar.pack(fill="x", padx=16, pady=(0, 4))
        self.str_bar.set(0)

        self.str_label = ctk.CTkLabel(sc, text="",
                                      font=ctk.CTkFont(size=12, weight="bold"),
                                      text_color=p["subtext"])
        self.str_label.pack(anchor="w", padx=16, pady=(0, 6))
        # Don't register str_label — its color is set dynamically by the score

        self.str_detail = self._reg_detail(
            ctk.CTkTextbox(sc, height=120,
                           font=ctk.CTkFont(family="Consolas", size=12),
                           fg_color=p["card"], text_color=p["detail_text"],
                           border_color=p["border"], border_width=1, corner_radius=8))
        self.str_detail.pack(fill="x", padx=16, pady=(0, 14))

        # ── Encrypt / Decrypt card ────────────────────────────────────────────
        ec = self._reg_card(make_card(self))
        ec.pack(fill="x", padx=20, pady=6)
        self._section_label(ec, "Encrypt / Decrypt Password")

        mr = ctk.CTkFrame(ec, fg_color="transparent")
        mr.pack(fill="x", padx=16, pady=(0, 8))
        method_lbl = self._inline_label(mr, "Method:")
        method_lbl.pack(side="left")

        self.method_var = ctk.StringVar(value="caesar")
        for lbl, val in [("Caesar", "caesar"), ("Vigenère", "vigenere"), ("Double-Layer 🔐", "double")]:
            rb = ctk.CTkRadioButton(mr, text=lbl, variable=self.method_var, value=val,
                                    font=ctk.CTkFont(size=12),
                                    command=self._update_key_ui)
            rb.pack(side="left", padx=12)
            self._reg_subtext(rb)

        kr = ctk.CTkFrame(ec, fg_color="transparent")
        kr.pack(fill="x", padx=16, pady=(0, 8))

        shift_lbl = self._inline_label(kr, "Shift:")
        shift_lbl.configure(width=46)
        shift_lbl.pack(side="left")

        self.shift_var2 = tk.IntVar(value=7)
        self.shift_entry = self._entry(kr, textvariable=self.shift_var2,
                                       width=60, height=34, font=ctk.CTkFont(size=13))
        self.shift_entry.pack(side="left", padx=(0, 20))

        kw_lbl = self._inline_label(kr, "Keyword:")
        kw_lbl.pack(side="left")
        self.kw_entry = self._entry(kr, width=150, height=34,
                                    placeholder_text="e.g. CIPHER",
                                    font=ctk.CTkFont(family="Consolas", size=13))
        self.kw_entry.pack(side="left", padx=(6, 0))

        bbr = ctk.CTkFrame(ec, fg_color="transparent")
        bbr.pack(fill="x", padx=16, pady=(0, 8))
        primary_btn(bbr, "🔒  Encrypt Password", self._encrypt_pw).pack(side="left", padx=(0, 8))
        primary_btn(bbr, "🔓  Decrypt Result",   self._decrypt_pw, "#238636", "#2ea043").pack(side="left")

        self._section_label(ec, "Result")
        self.enc_out = self._result_box(ec, 80)

        svr = ctk.CTkFrame(ec, fg_color="transparent")
        svr.pack(fill="x", padx=16, pady=(0, 14))
        lbl_lbl = self._inline_label(svr, "Label:")
        lbl_lbl.pack(side="left")
        self.vault_lbl_entry = self._entry(svr, width=160, height=34,
                                           placeholder_text="e.g. Gmail",
                                           font=ctk.CTkFont(size=13))
        self.vault_lbl_entry.pack(side="left", padx=8)
        primary_btn(svr, "💾  Save to Vault", self._save_vault, "#6e40c9", "#8957e5").pack(side="left")

        # ── Vault card ────────────────────────────────────────────────────────
        vc = self._reg_card(make_card(self))
        vc.pack(fill="x", padx=20, pady=(6, 24))

        vh = ctk.CTkFrame(vc, fg_color="transparent")
        vh.pack(fill="x")
        self._section_label(vh, "Password Vault")
        primary_btn(vh, "🔄 Refresh", self._refresh_vault,
                    "#0969da", "#1158c7", width=90).pack(side="right", padx=16, pady=10)

        self.vault_box = self._reg_detail(
            ctk.CTkTextbox(vc, height=210,
                           font=ctk.CTkFont(family="Consolas", size=12),
                           fg_color=p["card"], text_color=p["detail_text"],
                           border_color=p["border"], border_width=1, corner_radius=8))
        self.vault_box.pack(fill="x", padx=16, pady=(0, 16))

        self._update_key_ui()
        self._refresh_vault()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _update_key_ui(self):
        m = self.method_var.get()
        self.shift_entry.configure(state="normal" if m in ("caesar", "double") else "disabled")
        self.kw_entry.configure(state="normal" if m in ("vigenere", "double") else "disabled")

    def _get_key(self):
        m = self.method_var.get()
        try:
            shift = int(self.shift_var2.get())
        except Exception:
            shift = 7
        kw = self.kw_entry.get().strip()
        if m == "caesar":   return m, shift
        if m == "vigenere": return m, kw
        return m, (shift, kw)

    def _check_strength(self):
        pw = self.pw_entry.get()
        if not pw:
            messagebox.showwarning("Input needed", "Enter a password to analyse.")
            return
        r = password_tool.strength_report(pw)
        score, rating = r["score"], r["rating"]
        self.str_bar.set(score / 100)
        clr = {"Very Strong": "#3fb950", "Strong": "#58a6ff",
               "Fair": "#f0883e", "Weak": "#f85149"}.get(rating, "#8b949e")
        self.str_bar.configure(progress_color=clr)
        emoji = {"Very Strong": "🟢", "Strong": "🔵", "Fair": "🟡", "Weak": "🔴"}.get(rating, "⚪")
        entropy = r["entropy"]
        self.str_label.configure(
            text=f"{emoji}  {rating}  —  {score}/100  |  Entropy: {entropy:.2f} bits/char",
            text_color=clr)
        lines = ["Checks:\n"]
        for check, passed in r["checks"].items():
            lines.append(f"  {'✔' if passed else '✖'}  {check.replace('_', ' ').title()}")
        if r["suggestions"]:
            lines.append("\nTips to improve:")
            for tip in r["suggestions"]:
                lines.append(f"  →  {tip}")
        self.str_detail.configure(state="normal")
        self.str_detail.delete("1.0", "end")
        self.str_detail.insert("1.0", "\n".join(lines))
        self.str_detail.configure(state="disabled")

    def _encrypt_pw(self):
        pw = self.pw_entry.get()
        if not pw:
            messagebox.showwarning("Input needed", "Enter a password first.")
            return
        m, k = self._get_key()
        try:
            enc = password_tool.encrypt_password(pw, m, k)
            self._last_encrypted = enc
            set_result(self.enc_out, f"[Encrypted | Method = {m}]\n{enc}")
        except Exception as e:
            messagebox.showerror("Encryption Error", str(e))

    def _decrypt_pw(self):
        if not self._last_encrypted:
            messagebox.showwarning("Nothing to decrypt",
                                   "Encrypt a password first, then click Decrypt Result.")
            return
        m, k = self._get_key()
        try:
            plain = password_tool.decrypt_password(self._last_encrypted, m, k)
            set_result(self.enc_out, f"[Decrypted | Method = {m}]\n{plain}")
        except Exception as e:
            messagebox.showerror("Decryption Error", str(e))

    def _save_vault(self):
        label = self.vault_lbl_entry.get().strip()
        if not label:
            messagebox.showwarning("Label needed", "Enter a label for this entry.")
            return
        pw = self.pw_entry.get()
        if not pw:
            messagebox.showwarning("Input needed", "Enter a password to save.")
            return
        m, k = self._get_key()
        try:
            enc = password_tool.encrypt_password(pw, m, k)
            password_tool.vault_add(label, enc, m)
            messagebox.showinfo("Saved ✔",
                                f"'{label}' saved to vault.\n\n"
                                "⚠  Your key is NOT stored — remember it!")
            self._refresh_vault()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _refresh_vault(self):
        vault = password_tool.vault_list()
        self.vault_box.configure(state="normal")
        self.vault_box.delete("1.0", "end")
        if not vault:
            self.vault_box.insert("1.0", "  Vault is empty — encrypt and save a password above.")
        else:
            header = f"  {'Label':<22}{'Method':<14}{'Encrypted':<40}{'Saved At'}"
            rows = [header, "  " + "─" * 94]
            for lbl, entry in vault.items():
                rows.append(f"  {lbl:<22}{entry['method']:<14}"
                            f"{entry['encrypted']:<40}{entry.get('saved_at', '')}")
            self.vault_box.insert("1.0", "\n".join(rows))
        self.vault_box.configure(state="disabled")


# ═══════════════════════════════════════════════════════════════════════════════
#  Panel 5 — About
# ═══════════════════════════════════════════════════════════════════════════════

class AboutPanel(BasePanel):
    def __init__(self, master):
        super().__init__(master)
        self._build()

    def _build(self):
        p = P()
        self._heading("ℹ️  About CryptX")

        about_text = """\
  CryptX  —  Classical Cryptography Suite
  ──────────────────────────────────────────────────────────────────

  SKILLS DEMONSTRATED
    ✔  Classical cipher algorithm implementation (Caesar, Vigenère)
    ✔  Frequency analysis — automated statistical cipher breaking
    ✔  Python tool development from scratch (modular architecture)
    ✔  Understanding of why modern encryption replaced classics
    ✔  Password strength analysis with Shannon entropy measurement
    ✔  Double-layer cipher encryption for stronger password protection
    ✔  File-backed encrypted password vault (JSON, no plaintext stored)

  THE CIPHERS
    Caesar (ROT-N)
        Shifts every letter by a fixed number (1–25).
        Key space: 25 possible keys.  Brute-forced in < 1 second.

    Vigenère
        Uses a keyword; each letter gets a different Caesar shift.
        Resisted cryptanalysis for ~300 years.
        Broken by Kasiski examination + Index of Coincidence analysis.

  BREAKING TECHNIQUES INCLUDED
    Brute Force          —  All 25 Caesar shifts shown simultaneously
    Frequency Analysis   —  Chi-squared scoring against English profile
    Kasiski Examination  —  Find repeated n-grams to estimate key length
    Index of Coincidence —  English IC ≈ 0.065 | Random IC ≈ 0.038

  WHY MODERN ENCRYPTION REPLACED CLASSICAL CIPHERS
    Caesar   : 25 keys              → cracked in milliseconds
    Vigenère : ~millions of keys    → cracked in hours
    AES-256  : 2^256 keys           → centuries with any known attack
    AES destroys all statistical structure — output looks like random data.

  PROJECT FILES
    app.py                —  This GUI application (CustomTkinter)
    main.py               —  CLI entry point
    caesar.py             —  Caesar cipher module
    vigenere.py           —  Vigenère cipher module
    frequency_analysis.py —  Statistical cipher-breaking algorithms
    password_tool.py      —  Password encryption & vault
    test_cipher.py        —  Automated test suite

  ──────────────────────────────────────────────────────────────────
  "A working cipher tool with frequency analysis is a great
   conversation starter in any security interview."
"""
        self.about_tb = self._reg_detail(
            ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=13),
                           fg_color=p["card"], text_color=p["detail_text"],
                           border_color=p["border"], border_width=1,
                           corner_radius=12, height=620))
        self.about_tb.pack(fill="both", padx=20, pady=(0, 24), expand=True)
        self.about_tb.insert("1.0", about_text)
        self.about_tb.configure(state="disabled")


# ═══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        app = CipherApp()
        app.mainloop()
    except KeyboardInterrupt:
        pass
