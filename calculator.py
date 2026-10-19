"""Basic four-function calculator with a tkinter window."""

import tkinter as tk
from tkinter import font as tkfont


class Calculator(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("계산기")
        self.minsize(280, 380)
        self.configure(bg="#1c1c1e")

        self._display = "0"
        self._stored: float | None = None
        self._pending: str | None = None
        self._fresh = True
        self._error = False

        self._build()
        self._render()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        display_font = tkfont.Font(family="Segoe UI", size=28)
        button_font = tkfont.Font(family="Segoe UI", size=16)

        self._label = tk.Label(
            self,
            text="0",
            anchor="e",
            bg="#1c1c1e",
            fg="#ffffff",
            font=display_font,
            padx=16,
            pady=24,
        )
        self._label.grid(row=0, column=0, sticky="nsew")

        pad = tk.Frame(self, bg="#1c1c1e", padx=8, pady=8)
        pad.grid(row=1, column=0, sticky="nsew")
        for col in range(4):
            pad.columnconfigure(col, weight=1, uniform="btn")
        for row in range(5):
            pad.rowconfigure(row, weight=1, uniform="btn")

        # [ C ] [ ± ] [   ] [ ÷ ]
        # [ 7 ] [ 8 ] [ 9 ] [ × ]
        # [ 4 ] [ 5 ] [ 6 ] [ − ]
        # [ 1 ] [ 2 ] [ 3 ] [ + ]
        # [ 0      ] [ . ] [ = ]
        digit = "#333333"
        op = "#ff9f0a"
        fn = "#a5a5a5"
        light = "#ffffff"
        dark = "#000000"

        layout = [
            [
                ("C", self._clear, fn, dark),
                ("±", self._negate, fn, dark),
                None,
                ("÷", lambda: self._operator("/"), op, light),
            ],
            [
                ("7", lambda: self._digit("7"), digit, light),
                ("8", lambda: self._digit("8"), digit, light),
                ("9", lambda: self._digit("9"), digit, light),
                ("×", lambda: self._operator("*"), op, light),
            ],
            [
                ("4", lambda: self._digit("4"), digit, light),
                ("5", lambda: self._digit("5"), digit, light),
                ("6", lambda: self._digit("6"), digit, light),
                ("−", lambda: self._operator("-"), op, light),
            ],
            [
                ("1", lambda: self._digit("1"), digit, light),
                ("2", lambda: self._digit("2"), digit, light),
                ("3", lambda: self._digit("3"), digit, light),
                ("+", lambda: self._operator("+"), op, light),
            ],
            [
                ("0", lambda: self._digit("0"), digit, light),
                None,
                (".", self._decimal, digit, light),
                ("=", self._equals, op, light),
            ],
        ]

        for r, row in enumerate(layout):
            for c, cell in enumerate(row):
                if cell is None:
                    continue
                text, command, bg, fg = cell
                button = tk.Button(
                    pad,
                    text=text,
                    command=command,
                    font=button_font,
                    bg=bg,
                    fg=fg,
                    activebackground=bg,
                    activeforeground=fg,
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                )
                button.grid(
                    row=r,
                    column=c,
                    columnspan=2 if text == "0" else 1,
                    sticky="nsew",
                    padx=4,
                    pady=4,
                )

    def _render(self) -> None:
        self._label.configure(text=self._display)

    def _reset_if_error(self) -> None:
        if self._error:
            self._clear()

    def _clear(self) -> None:
        self._display = "0"
        self._stored = None
        self._pending = None
        self._fresh = True
        self._error = False
        self._render()

    def _digit(self, digit: str) -> None:
        self._reset_if_error()
        if self._fresh or self._display == "0":
            self._display = digit
            self._fresh = False
        else:
            self._display += digit
        self._render()

    def _decimal(self) -> None:
        self._reset_if_error()
        if self._fresh:
            self._display = "0."
            self._fresh = False
        elif "." not in self._display:
            self._display += "."
        self._render()

    def _negate(self) -> None:
        self._reset_if_error()
        if self._display in ("0", "0."):
            return
        if self._display.startswith("-"):
            self._display = self._display[1:]
        else:
            self._display = "-" + self._display
        self._render()

    def _current(self) -> float:
        return float(self._display)

    def _format(self, value: float) -> str:
        if value != value or value in (float("inf"), float("-inf")):
            return "Error"
        text = f"{value:.12g}"
        if text in ("-0", "-0.0"):
            return "0"
        return text

    def _apply(self, operator: str, left: float, right: float) -> float | None:
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            if right == 0:
                return None
            return left / right
        raise ValueError(operator)

    def _commit(self) -> bool:
        """Apply the pending operator. Return False on divide-by-zero."""
        if self._pending is None or self._stored is None:
            self._stored = self._current()
            return True
        if self._fresh:
            return True
        result = self._apply(self._pending, self._stored, self._current())
        if result is None:
            self._fail()
            return False
        shown = self._format(result)
        if shown == "Error":
            self._fail()
            return False
        self._stored = result
        self._display = shown
        self._fresh = True
        self._render()
        return True

    def _fail(self) -> None:
        self._display = "Error"
        self._stored = None
        self._pending = None
        self._fresh = True
        self._error = True
        self._render()

    def _operator(self, operator: str) -> None:
        if self._error:
            return
        if not self._commit():
            return
        self._pending = operator
        self._fresh = True

    def _equals(self) -> None:
        if self._error:
            return
        if not self._commit():
            return
        self._pending = None
        self._fresh = True


if __name__ == "__main__":
    Calculator().mainloop()
