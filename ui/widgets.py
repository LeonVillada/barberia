"""
widgets.py - Componentes reutilizables de UI
"""

import tkinter as tk
from tkinter import ttk
from core.styles import COLORS, FONTS, PADDING


# ── Botón personalizado ───────────────────────────────────────────────────────
class ModernButton(tk.Button):
    def __init__(self, parent, text="", command=None, style="primary",
                 width=None, **kwargs):
        styles = {
            "primary":   {"bg": COLORS["accent"],       "fg": COLORS["text_white"],    "abg": COLORS["accent_hover"]},
            "success":   {"bg": COLORS["accent_green"],  "fg": COLORS["text_white"],    "abg": "#27AE60"},
            "warning":   {"bg": COLORS["accent_orange"], "fg": COLORS["text_white"],    "abg": "#D68910"},
            "info":      {"bg": COLORS["accent_blue"],   "fg": COLORS["text_white"],    "abg": "#2980B9"},
            "danger":    {"bg": "#E74C3C",               "fg": COLORS["text_white"],    "abg": "#C0392B"},
            "ghost":     {"bg": COLORS["bg_light"],      "fg": COLORS["text_primary"],  "abg": COLORS["bg_card"]},
        }
        s = styles.get(style, styles["primary"])

        kw = dict(
            text=text, command=command,
            bg=s["bg"], fg=s["fg"],
            font=FONTS["button"],
            relief="flat", bd=0,
            padx=PADDING["md"], pady=PADDING["sm"],
            cursor="hand2", activebackground=s["abg"],
            activeforeground=s["fg"],
        )
        if width:
            kw["width"] = width
        kw.update(kwargs)

        super().__init__(parent, **kw)
        self._abg = s["abg"]
        self._bg  = s["bg"]
        self.bind("<Enter>", lambda e: self.config(bg=self._abg))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))


# ── Etiqueta de título ────────────────────────────────────────────────────────
class TitleLabel(tk.Label):
    def __init__(self, parent, text="", **kwargs):
        super().__init__(
            parent, text=text, font=FONTS["title"],
            bg=COLORS["bg_medium"], fg=COLORS["text_white"],
            **kwargs
        )


class SubtitleLabel(tk.Label):
    def __init__(self, parent, text="", **kwargs):
        super().__init__(
            parent, text=text, font=FONTS["subtitle"],
            bg=COLORS["bg_medium"], fg=COLORS["accent"],
            **kwargs
        )


# ── Card (frame con bordes redondeados simulados) ─────────────────────────────
class Card(tk.Frame):
    def __init__(self, parent, **kwargs):
        kw = dict(bg=COLORS["bg_card"], padx=PADDING["md"], pady=PADDING["md"])
        kw.update(kwargs)
        super().__init__(parent, **kw)


# ── Campo de entrada etiquetado ───────────────────────────────────────────────
class LabeledEntry(tk.Frame):
    def __init__(self, parent, label="", show=None, **kwargs):
        super().__init__(parent, bg=COLORS["bg_medium"], **kwargs)

        tk.Label(
            self, text=label, font=FONTS["small"],
            bg=COLORS["bg_medium"], fg=COLORS["text_secondary"]
        ).pack(anchor="w")

        self.var = tk.StringVar()
        entry_kw = dict(
            textvariable=self.var,
            font=FONTS["body"],
            bg=COLORS["bg_input"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["bg_light"],
            highlightcolor=COLORS["accent"],
        )
        if show:
            entry_kw["show"] = show

        self.entry = tk.Entry(self, **entry_kw)
        self.entry.pack(fill="x", ipady=6)

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)

    def clear(self):
        self.var.set("")


# ── Combobox personalizado ────────────────────────────────────────────────────
class LabeledCombo(tk.Frame):
    def __init__(self, parent, label="", values=None, **kwargs):
        super().__init__(parent, bg=COLORS["bg_medium"], **kwargs)

        tk.Label(
            self, text=label, font=FONTS["small"],
            bg=COLORS["bg_medium"], fg=COLORS["text_secondary"]
        ).pack(anchor="w")

        self.var = tk.StringVar()
        self.combo = ttk.Combobox(
            self, textvariable=self.var,
            values=values or [], state="readonly",
            font=FONTS["body"],
        )
        self.combo.pack(fill="x", ipady=4)

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)

    def set_values(self, values):
        self.combo["values"] = values
        self.var.set("")


# ── Treeview con scrollbars ───────────────────────────────────────────────────
class ScrollableTreeview(tk.Frame):
    def __init__(self, parent, columns: list[tuple], height=10, **kwargs):
        """
        columns: lista de (col_id, col_heading, width)
        """
        super().__init__(parent, bg=COLORS["bg_medium"], **kwargs)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview",
            background=COLORS["bg_input"],
            foreground=COLORS["text_primary"],
            fieldbackground=COLORS["bg_input"],
            rowheight=28,
            font=FONTS["body"],
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=COLORS["bg_card"],
            foreground=COLORS["accent"],
            font=FONTS["body_bold"],
            relief="flat",
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", COLORS["text_white"])],
        )

        self.tree = ttk.Treeview(
            self,
            columns=[c[0] for c in columns],
            show="headings",
            height=height,
            style="Custom.Treeview",
            selectmode="browse",
        )

        for col_id, heading, width in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor="center")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insert(self, values: tuple, tags=()):
        self.tree.insert("", "end", values=values, tags=tags)

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0], "values")

    def bind_double_click(self, callback):
        self.tree.bind("<Double-1>", callback)

    def tag_configure(self, tag, **kwargs):
        self.tree.tag_configure(tag, **kwargs)


# ── Separador ─────────────────────────────────────────────────────────────────
class Divider(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_light"], height=1, **kwargs)


# ── Badge de estado ───────────────────────────────────────────────────────────
STATE_COLORS = {
    "Pendiente":  COLORS["estado_pendiente"],
    "Confirmada": COLORS["estado_confirmada"],
    "Cancelada":  COLORS["estado_cancelada"],
    "Finalizada": COLORS["estado_finalizada"],
    "Activo":     COLORS["accent_green"],
    "Inactivo":   "#E74C3C",
}
