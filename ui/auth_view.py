"""
auth_view.py - Pantallas de Login y Registro
"""

import tkinter as tk
from tkinter import messagebox
from core.styles import COLORS, FONTS, PADDING
from core import database as db
from ui.widgets import ModernButton, LabeledEntry


class AuthView(tk.Frame):
    """Contenedor principal que alterna entre Login y Registro."""

    def __init__(self, parent, on_login_success):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.on_login_success = on_login_success
        self._show_login()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _show_login(self):
        self._clear()
        LoginPanel(self, on_success=self.on_login_success,
                   on_register=self._show_register).pack(expand=True)

    def _show_register(self):
        self._clear()
        RegisterPanel(self, on_success=self._show_login,
                      on_back=self._show_login).pack(expand=True)


# ── Panel de Login ─────────────────────────────────────────────────────────────
class LoginPanel(tk.Frame):
    def __init__(self, parent, on_success, on_register):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.on_success = on_success
        self.on_register = on_register
        self._build()

    def _build(self):
        # ── Logo / cabecera ──────────────────────────────────────────────────
        header = tk.Frame(self, bg=COLORS["bg_dark"])
        header.pack(pady=(60, 30))

        tk.Label(
            header, text="✂", font=("Segoe UI", 48),
            bg=COLORS["bg_dark"], fg=COLORS["accent"]
        ).pack()
        tk.Label(
            header, text="BARBERÍA PRO",
            font=FONTS["logo"], bg=COLORS["bg_dark"],
            fg=COLORS["text_white"]
        ).pack()
        tk.Label(
            header, text="Sistema de Gestión de Agenda",
            font=FONTS["small"], bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"]
        ).pack(pady=(4, 0))

        # ── Card del formulario ───────────────────────────────────────────────
        card = tk.Frame(self, bg=COLORS["bg_medium"],
                        padx=PADDING["xl"], pady=PADDING["xl"])
        card.pack(ipadx=PADDING["lg"], ipady=PADDING["lg"])

        tk.Label(
            card, text="Iniciar Sesión",
            font=FONTS["subtitle"], bg=COLORS["bg_medium"],
            fg=COLORS["text_white"]
        ).pack(pady=(0, PADDING["md"]))

        self.email_field = LabeledEntry(card, label="Correo electrónico")
        self.email_field.pack(fill="x", pady=PADDING["sm"])

        self.pass_field = LabeledEntry(card, label="Contraseña", show="●")
        self.pass_field.pack(fill="x", pady=PADDING["sm"])

        ModernButton(
            card, text="  Ingresar  ", command=self._login,
            style="primary"
        ).pack(pady=(PADDING["lg"], PADDING["sm"]), fill="x")

        # ── Enlace a registro ─────────────────────────────────────────────────
        sep = tk.Frame(card, bg=COLORS["bg_medium"])
        sep.pack(pady=(PADDING["sm"], 0))

        tk.Label(
            sep, text="¿No tienes cuenta?",
            font=FONTS["small"], bg=COLORS["bg_medium"],
            fg=COLORS["text_secondary"]
        ).pack(side="left")

        reg_btn = tk.Label(
            sep, text=" Regístrate",
            font=("Segoe UI", 9, "underline"),
            bg=COLORS["bg_medium"], fg=COLORS["accent"],
            cursor="hand2"
        )
        reg_btn.pack(side="left")
        reg_btn.bind("<Button-1>", lambda e: self.on_register())

        # Sugerencia de admin
        tk.Label(
            card, text="Admin: admin@barberia.com / admin123",
            font=FONTS["small"], bg=COLORS["bg_medium"],
            fg=COLORS["text_muted"]
        ).pack(pady=(PADDING["md"], 0))

        # Enter para hacer login
        self.email_field.entry.bind("<Return>", lambda e: self._login())
        self.pass_field.entry.bind("<Return>",  lambda e: self._login())

    def _login(self):
        email = self.email_field.get().strip()
        password = self.pass_field.get().strip()

        if not email or not password:
            messagebox.showwarning("Campos requeridos",
                                   "Por favor ingresa tu correo y contraseña.")
            return

        user = db.authenticate_user(email, password)
        if not user:
            messagebox.showerror("Error de acceso",
                                 "Correo o contraseña incorrectos.")
            return

        import logging
        logging.getLogger(__name__).info(
            "Login exitoso: %s (%s)", user["email"], user["rol"]
        )
        self.on_success(user)


# ── Panel de Registro ──────────────────────────────────────────────────────────
class RegisterPanel(tk.Frame):
    def __init__(self, parent, on_success, on_back):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.on_success = on_success
        self.on_back = on_back
        self._build()

    def _build(self):
        tk.Label(
            self, text="✂  BARBERÍA PRO",
            font=FONTS["logo"], bg=COLORS["bg_dark"],
            fg=COLORS["accent"]
        ).pack(pady=(40, 0))

        card = tk.Frame(self, bg=COLORS["bg_medium"],
                        padx=PADDING["xl"], pady=PADDING["xl"])
        card.pack(pady=PADDING["lg"], ipadx=PADDING["lg"], ipady=PADDING["md"])

        tk.Label(
            card, text="Crear Cuenta",
            font=FONTS["subtitle"], bg=COLORS["bg_medium"],
            fg=COLORS["text_white"]
        ).pack(pady=(0, PADDING["md"]))

        self.nombre = LabeledEntry(card, label="Nombre completo")
        self.nombre.pack(fill="x", pady=4)

        self.telefono = LabeledEntry(card, label="Teléfono")
        self.telefono.pack(fill="x", pady=4)

        self.email = LabeledEntry(card, label="Correo electrónico")
        self.email.pack(fill="x", pady=4)

        self.password = LabeledEntry(card, label="Contraseña", show="●")
        self.password.pack(fill="x", pady=4)

        self.confirm = LabeledEntry(card, label="Confirmar contraseña", show="●")
        self.confirm.pack(fill="x", pady=4)

        ModernButton(
            card, text="  Crear Cuenta  ", command=self._register,
            style="success"
        ).pack(pady=(PADDING["lg"], PADDING["sm"]), fill="x")

        back = tk.Label(
            card, text="← Volver al Login",
            font=("Segoe UI", 9, "underline"),
            bg=COLORS["bg_medium"], fg=COLORS["accent"],
            cursor="hand2"
        )
        back.pack()
        back.bind("<Button-1>", lambda e: self.on_back())

    def _register(self):
        nombre   = self.nombre.get().strip()
        telefono = self.telefono.get().strip()
        email    = self.email.get().strip()
        pwd      = self.password.get().strip()
        confirm  = self.confirm.get().strip()

        if not all([nombre, telefono, email, pwd]):
            messagebox.showwarning("Campos requeridos",
                                   "Por favor completa todos los campos.")
            return

        if "@" not in email:
            messagebox.showwarning("Email inválido",
                                   "Ingresa un correo electrónico válido.")
            return

        if pwd != confirm:
            messagebox.showerror("Contraseñas no coinciden",
                                 "Las contraseñas no son iguales.")
            return

        if len(pwd) < 6:
            messagebox.showwarning("Contraseña débil",
                                   "La contraseña debe tener al menos 6 caracteres.")
            return

        ok = db.create_user(nombre, telefono, email, pwd)
        if not ok:
            messagebox.showerror("Email en uso",
                                 "Ya existe una cuenta con ese correo.")
            return

        messagebox.showinfo("¡Cuenta creada!",
                            f"Bienvenido {nombre}.\nYa puedes iniciar sesión.")
        self.on_success()
