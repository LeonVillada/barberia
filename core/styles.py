"""
styles.py - Paleta de colores, fuentes y constantes de diseño
"""

# ── Paleta principal ──────────────────────────────────────────────────────────
COLORS = {
    # Fondos
    "bg_dark":       "#1A1A2E",
    "bg_medium":     "#16213E",
    "bg_card":       "#0F3460",
    "bg_light":      "#243B55",
    "bg_input":      "#1E2A3A",

    # Acentos
    "accent":        "#E94560",
    "accent_hover":  "#C73652",
    "accent_green":  "#2ECC71",
    "accent_orange": "#F39C12",
    "accent_blue":   "#3498DB",

    # Texto
    "text_primary":  "#EAEAEA",
    "text_secondary":"#A0AEC0",
    "text_muted":    "#718096",
    "text_white":    "#FFFFFF",

    # Estados de cita
    "estado_pendiente":   "#F39C12",
    "estado_confirmada":  "#2ECC71",
    "estado_cancelada":   "#E74C3C",
    "estado_finalizada":  "#95A5A6",

    # Sidebar
    "sidebar_bg":    "#0D1B2A",
    "sidebar_hover": "#1A3047",
    "sidebar_active":"#E94560",
}

# ── Fuentes ───────────────────────────────────────────────────────────────────
FONTS = {
    "title":    ("Segoe UI", 22, "bold"),
    "subtitle": ("Segoe UI", 14, "bold"),
    "heading":  ("Segoe UI", 12, "bold"),
    "body":     ("Segoe UI", 10),
    "body_bold":("Segoe UI", 10, "bold"),
    "small":    ("Segoe UI", 9),
    "button":   ("Segoe UI", 10, "bold"),
    "nav":      ("Segoe UI", 11),
    "logo":     ("Segoe UI", 18, "bold"),
    "mono":     ("Consolas",  10),
}

# ── Dimensiones ───────────────────────────────────────────────────────────────
WINDOW = {
    "width":  1100,
    "height":  680,
    "min_w":   900,
    "min_h":   600,
    "sidebar": 210,
}

PADDING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 40,
}

# ── Categorías de servicios ───────────────────────────────────────────────────
SERVICE_CATEGORIES = ["corte", "barba", "combo", "coloración", "tratamiento", "otro"]

# ── Estados posibles de una cita ─────────────────────────────────────────────
APPOINTMENT_STATES = ["Pendiente", "Confirmada", "Cancelada", "Finalizada"]

# ── Horarios permitidos ───────────────────────────────────────────────────────
WORK_HOURS = [f"{h:02d}:{m:02d}" for h in range(6, 22) for m in (0, 30)]
