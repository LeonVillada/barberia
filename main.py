"""
main.py - Punto de entrada de la aplicación Barbería Pro
Gestiona el ciclo de vida, el routing entre vistas y la ventana principal.
"""

import sys
import os
import logging
import tkinter as tk
from tkinter import messagebox

# ── Configuración de logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s  %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("main")

# ── Agregar el directorio raíz al path (compatible PyInstaller) ───────────────
if getattr(sys, "frozen", False):
    ROOT = sys._MEIPASS  # type: ignore[attr-defined]
else:
    ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# ── Imports internos ──────────────────────────────────────────────────────────
from core import database as db
from core.styles import COLORS, FONTS, WINDOW


# ══════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    """Ventana raíz y controlador de rutas."""

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._init_db()
        self._current_view = None
        self._show_auth()

    # ── Configuración de ventana ──────────────────────────────────────────────
    def _setup_window(self):
        self.title("Barbería Pro - Sistema de Agenda")
        self.geometry(f"{WINDOW['width']}x{WINDOW['height']}")
        self.minsize(WINDOW["min_w"], WINDOW["min_h"])
        self.configure(bg=COLORS["bg_dark"])
        self.resizable(True, True)

        # Centrar en pantalla
        self.update_idletasks()
        w = WINDOW["width"]
        h = WINDOW["height"]
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Estilo global de ttk
        from tkinter import ttk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["bg_input"],
            background=COLORS["bg_input"],
            foreground=COLORS["text_primary"],
            selectbackground=COLORS["accent"],
            selectforeground=COLORS["text_white"],
            arrowcolor=COLORS["text_secondary"],
        )
        style.map("TCombobox", fieldbackground=[("readonly", COLORS["bg_input"])])
        style.configure(
            "TScrollbar",
            background=COLORS["bg_light"],
            troughcolor=COLORS["bg_dark"],
            bordercolor=COLORS["bg_dark"],
            arrowcolor=COLORS["text_muted"],
        )

        logger.info("Ventana configurada (%dx%d)", w, h)

    # ── Inicialización de la base de datos ────────────────────────────────────
    def _init_db(self):
        try:
            db.init_database()
            logger.info("Base de datos inicializada correctamente.")
        except Exception as e:
            logger.exception("Error al inicializar la base de datos: %s", e)
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudo inicializar la base de datos:\n{e}"
            )
            self.destroy()

    # ── Routing entre vistas ──────────────────────────────────────────────────
    def _clear(self):
        if self._current_view:
            self._current_view.destroy()
            self._current_view = None

    def _show_auth(self):
        self._clear()
        from ui.auth_view import AuthView
        self._current_view = AuthView(self, on_login_success=self._on_login)
        self._current_view.pack(fill="both", expand=True)
        logger.info("Mostrando pantalla de autenticación.")

    def _on_login(self, user: dict):
        logger.info("Usuario autenticado: %s rol=%s", user["email"], user["rol"])
        if user["rol"] == "admin":
            self._show_admin(user)
        else:
            self._show_client(user)

    def _show_admin(self, user: dict):
        self._clear()
        from ui.admin_view import AdminView
        self._current_view = AdminView(
            self, user=user, on_logout=self._show_auth
        )
        self._current_view.pack(fill="both", expand=True)
        self.title(f"Barbería Pro - Panel Administrador | {user['nombre']}")
        logger.info("Panel administrador cargado.")

    def _show_client(self, user: dict):
        self._clear()
        from ui.client_view import ClientView
        self._current_view = ClientView(
            self, user=user, on_logout=self._show_auth
        )
        self._current_view.pack(fill="both", expand=True)
        self.title(f"Barbería Pro - Bienvenido {user['nombre']}")
        logger.info("Panel cliente cargado.")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("Aplicación cerrada por el usuario.")
    except Exception as e:
        logger.exception("Error fatal: %s", e)
        messagebox.showerror("Error fatal", str(e))
