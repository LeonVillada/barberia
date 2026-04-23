"""
client_view.py - Panel del Cliente
Reservar cita, ver calendario de disponibilidad, gestionar citas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta, date
import calendar
from core.styles import COLORS, FONTS, PADDING, APPOINTMENT_STATES
from core import database as db
from ui.widgets import (ModernButton, LabeledEntry, ScrollableTreeview,
                         Divider, STATE_COLORS)


# ══════════════════════════════════════════════════════════════════════════════
class ClientView(tk.Frame):
    """Panel principal del cliente con sidebar."""

    SECTIONS = [
        ("🏠", "Inicio",           "inicio"),
        ("📅", "Reservar Cita",    "reservar"),
        ("📋", "Mis Citas",        "mis_citas"),
        ("👤", "Mi Perfil",        "perfil"),
    ]

    def __init__(self, parent, user: dict, on_logout):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.user = user
        self.on_logout = on_logout
        self._build()

    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self._build_sidebar()
        self._content = tk.Frame(self, bg=COLORS["bg_medium"])
        self._content.grid(row=0, column=1, sticky="nsew")
        self._navigate("inicio")

    def _build_sidebar(self):
        sb = tk.Frame(self, bg=COLORS["sidebar_bg"], width=200)
        sb.grid(row=0, column=0, sticky="ns")
        sb.grid_propagate(False)

        tk.Label(sb, text="✂", font=("Segoe UI", 32),
                 bg=COLORS["sidebar_bg"], fg=COLORS["accent_green"]).pack(pady=(PADDING["lg"], 0))
        tk.Label(sb, text="BARBERÍA PRO", font=("Segoe UI", 10, "bold"),
                 bg=COLORS["sidebar_bg"], fg=COLORS["text_white"]).pack()
        tk.Label(sb, text=f"👋 {self.user['nombre'].split()[0]}",
                 font=FONTS["small"], bg=COLORS["sidebar_bg"],
                 fg=COLORS["text_muted"]).pack(pady=(0, PADDING["md"]))

        Divider(sb).pack(fill="x", padx=PADDING["sm"])

        self._nav_buttons = {}
        for icon, label, key in self.SECTIONS:
            btn = tk.Button(
                sb, text=f"  {icon}  {label}",
                font=FONTS["nav"], anchor="w",
                bg=COLORS["sidebar_bg"], fg=COLORS["text_secondary"],
                relief="flat", bd=0, padx=PADDING["md"], pady=10,
                cursor="hand2",
                command=lambda k=key: self._navigate(k),
                activebackground=COLORS["sidebar_hover"],
                activeforeground=COLORS["text_white"],
            )
            btn.pack(fill="x")
            self._nav_buttons[key] = btn

        tk.Frame(sb, bg=COLORS["sidebar_bg"]).pack(expand=True)
        Divider(sb).pack(fill="x", padx=PADDING["sm"])
        ModernButton(
            sb, text="  🚪 Cerrar Sesión",
            command=self.on_logout, style="danger"
        ).pack(fill="x", pady=PADDING["sm"], padx=PADDING["sm"])

    def _navigate(self, section: str):
        for key, btn in self._nav_buttons.items():
            if key == section:
                btn.config(bg=COLORS["accent_green"], fg=COLORS["text_white"])
            else:
                btn.config(bg=COLORS["sidebar_bg"], fg=COLORS["text_secondary"])

        for w in self._content.winfo_children():
            w.destroy()

        sections_map = {
            "inicio":    WelcomePanel,
            "reservar":  BookingPanel,
            "mis_citas": MisCitasPanel,
            "perfil":    PerfilPanel,
        }
        cls = sections_map.get(section, WelcomePanel)
        if section == "perfil":
            cls(self._content, self.user).pack(fill="both", expand=True)
        else:
            cls(self._content, self.user).pack(fill="both", expand=True)


# ══════════════════════════════════════════════════════════════════════════════
class WelcomePanel(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self.user = user
        self._build()

    def _build(self):
        # Bienvenida
        tk.Label(
            self, text=f"¡Bienvenido, {self.user['nombre'].split()[0]}! 👋",
            font=FONTS["title"], bg=COLORS["bg_medium"], fg=COLORS["text_white"]
        ).pack(anchor="w", padx=PADDING["lg"], pady=(PADDING["xl"], 0))

        tk.Label(
            self, text="Gestiona tus citas en Barbería Pro",
            font=FONTS["body"], bg=COLORS["bg_medium"], fg=COLORS["text_secondary"]
        ).pack(anchor="w", padx=PADDING["lg"])

        Divider(self).pack(fill="x", padx=PADDING["lg"], pady=PADDING["md"])

        # Tarjetas de acceso rápido
        grid = tk.Frame(self, bg=COLORS["bg_medium"])
        grid.pack(padx=PADDING["lg"], pady=PADDING["md"])

        citas_df = db.get_appointments_by_client(self.user["id"])
        total    = len(citas_df)
        pendientes = len(citas_df[citas_df["estado"] == "Pendiente"]) if total > 0 else 0
        proxima    = None
        hoy = datetime.now().strftime("%Y-%m-%d")
        if total > 0:
            futuras = citas_df[
                (citas_df["fecha"] >= hoy) &
                (citas_df["estado"].isin(["Pendiente", "Confirmada"]))
            ].sort_values("fecha")
            if not futuras.empty:
                proxima = futuras.iloc[0]

        quick_cards = [
            ("📅", "Mis Citas",       str(total),      COLORS["accent_blue"]),
            ("⏳", "Pendientes",      str(pendientes),  COLORS["accent_orange"]),
        ]
        for i, (icon, label, val, color) in enumerate(quick_cards):
            c = tk.Frame(grid, bg=COLORS["bg_card"],
                         padx=PADDING["xl"], pady=PADDING["lg"])
            c.grid(row=0, column=i, padx=8)
            tk.Label(c, text=icon, font=("Segoe UI", 28),
                     bg=COLORS["bg_card"], fg=color).pack()
            tk.Label(c, text=val, font=("Segoe UI", 22, "bold"),
                     bg=COLORS["bg_card"], fg=color).pack()
            tk.Label(c, text=label, font=FONTS["small"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack()

        # Próxima cita
        if proxima is not None:
            tk.Label(
                self, text="📌 Próxima Cita",
                font=FONTS["subtitle"], bg=COLORS["bg_medium"], fg=COLORS["accent"]
            ).pack(anchor="w", padx=PADDING["lg"], pady=(PADDING["lg"], PADDING["sm"]))

            card = tk.Frame(self, bg=COLORS["bg_card"],
                            padx=PADDING["lg"], pady=PADDING["lg"])
            card.pack(anchor="w", padx=PADDING["lg"])

            info = [
                ("Barbero",  proxima["barbero_nombre"]),
                ("Servicio", proxima["servicio_nombre"]),
                ("Fecha",    proxima["fecha"]),
                ("Hora",     proxima["hora_inicio"]),
                ("Estado",   proxima["estado"]),
                ("Precio",   f"${proxima['precio']:,.0f}"),
            ]
            for label, val in info:
                row = tk.Frame(card, bg=COLORS["bg_card"])
                row.pack(anchor="w", pady=2)
                tk.Label(row, text=f"{label}:", font=FONTS["body_bold"],
                         bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                         width=10, anchor="w").pack(side="left")
                tk.Label(row, text=val, font=FONTS["body"],
                         bg=COLORS["bg_card"], fg=COLORS["text_white"]).pack(side="left")


# ══════════════════════════════════════════════════════════════════════════════
class BookingPanel(tk.Frame):
    """Wizard de 3 pasos para reservar una cita."""

    def __init__(self, parent, user):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self.user = user
        self._step = 1
        self._sel_barber = None
        self._sel_service = None
        self._sel_date = None
        self._sel_slot = None
        self._build()

    def _build(self):
        # Cabecera
        tk.Label(
            self, text="📅  Reservar Cita",
            font=FONTS["title"], bg=COLORS["bg_medium"], fg=COLORS["text_white"]
        ).pack(anchor="w", padx=PADDING["lg"], pady=(PADDING["lg"], 0))

        # Indicador de pasos
        self._steps_bar = tk.Frame(self, bg=COLORS["bg_medium"])
        self._steps_bar.pack(fill="x", padx=PADDING["lg"], pady=PADDING["sm"])

        Divider(self).pack(fill="x", padx=PADDING["lg"])

        self._step_content = tk.Frame(self, bg=COLORS["bg_medium"])
        self._step_content.pack(fill="both", expand=True,
                                padx=PADDING["lg"], pady=PADDING["md"])

        self._show_step(1)

    def _update_steps_bar(self):
        for w in self._steps_bar.winfo_children():
            w.destroy()
        steps = ["1. Barbero", "2. Servicio", "3. Fecha y Hora", "4. Confirmar"]
        for i, label in enumerate(steps, 1):
            color = COLORS["accent"] if i == self._step else (
                COLORS["accent_green"] if i < self._step else COLORS["text_muted"]
            )
            tk.Label(
                self._steps_bar, text=label,
                font=FONTS["body_bold"] if i == self._step else FONTS["body"],
                bg=COLORS["bg_medium"], fg=color
            ).pack(side="left", padx=PADDING["md"])
            if i < 4:
                tk.Label(self._steps_bar, text="→", font=FONTS["body"],
                         bg=COLORS["bg_medium"], fg=COLORS["text_muted"]).pack(side="left")

    def _show_step(self, step: int):
        self._step = step
        self._update_steps_bar()
        for w in self._step_content.winfo_children():
            w.destroy()

        if step == 1:
            self._build_step1()
        elif step == 2:
            self._build_step2()
        elif step == 3:
            self._build_step3()
        elif step == 4:
            self._build_step4()

    # ── Paso 1: Seleccionar barbero ───────────────────────────────────────────
    def _build_step1(self):
        frame = self._step_content
        tk.Label(frame, text="Selecciona un Barbero",
                 font=FONTS["subtitle"], bg=COLORS["bg_medium"],
                 fg=COLORS["text_white"]).pack(anchor="w", pady=(0, PADDING["md"]))

        grid = tk.Frame(frame, bg=COLORS["bg_medium"])
        grid.pack(fill="x")

        barbers = db.get_all_barbers(only_active=True)
        for i, (_, barber) in enumerate(barbers.iterrows()):
            card = tk.Frame(grid, bg=COLORS["bg_card"],
                            padx=PADDING["lg"], pady=PADDING["lg"],
                            cursor="hand2")
            card.grid(row=i // 3, column=i % 3,
                      padx=8, pady=8, sticky="ew")
            grid.grid_columnconfigure(i % 3, weight=1)

            tk.Label(card, text="💈", font=("Segoe UI", 32),
                     bg=COLORS["bg_card"], fg=COLORS["accent"]).pack()
            tk.Label(card, text=barber["nombre"], font=FONTS["body_bold"],
                     bg=COLORS["bg_card"], fg=COLORS["text_white"]).pack()
            tk.Label(card, text=barber["especialidad"], font=FONTS["small"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack()
            tk.Label(
                card,
                text=f"🕐 {barber['hora_inicio']} - {barber['hora_fin']}",
                font=FONTS["small"],
                bg=COLORS["bg_card"], fg=COLORS["text_muted"]
            ).pack(pady=(4, 8))

            ModernButton(
                card, text="Seleccionar",
                command=lambda b=barber.to_dict(): self._select_barber(b),
                style="primary"
            ).pack()

    def _select_barber(self, barber: dict):
        self._sel_barber = barber
        self._show_step(2)

    # ── Paso 2: Seleccionar servicio ──────────────────────────────────────────
    def _build_step2(self):
        frame = self._step_content

        tk.Label(frame, text=f"Barbero: {self._sel_barber['nombre']}",
                 font=FONTS["body"], bg=COLORS["bg_medium"],
                 fg=COLORS["accent"]).pack(anchor="w")
        tk.Label(frame, text="Selecciona un Servicio",
                 font=FONTS["subtitle"], bg=COLORS["bg_medium"],
                 fg=COLORS["text_white"]).pack(anchor="w", pady=(0, PADDING["md"]))

        cols = [
            ("id",       "ID",       40),
            ("nombre",   "Servicio", 200),
            ("precio",   "Precio",   100),
            ("duracion", "Duración", 100),
            ("categoria","Categoría",120),
        ]
        tree_frame = tk.Frame(frame, bg=COLORS["bg_medium"])
        tree_frame.pack(fill="both", expand=True)
        self.svc_tree = ScrollableTreeview(tree_frame, cols, height=12)
        self.svc_tree.pack(fill="both", expand=True)

        services = db.get_all_services(only_active=True)
        for _, svc in services.iterrows():
            self.svc_tree.insert((
                svc["id"], svc["nombre"],
                f"${svc['precio']:,.0f}",
                f"{svc['duracion_min']} min",
                svc["categoria"]
            ))

        btn_row = tk.Frame(frame, bg=COLORS["bg_medium"])
        btn_row.pack(fill="x", pady=PADDING["md"])
        ModernButton(btn_row, text="← Atrás",
                     command=lambda: self._show_step(1), style="ghost").pack(side="left")
        ModernButton(btn_row, text="Siguiente →",
                     command=self._confirm_service, style="primary").pack(side="right")

    def _confirm_service(self):
        sel = self.svc_tree.get_selected()
        if not sel:
            messagebox.showinfo("Sin selección", "Selecciona un servicio.")
            return
        sid = int(sel[0])
        self._sel_service = db.get_service_by_id(sid)
        self._show_step(3)

    # ── Paso 3: Calendario y hora ─────────────────────────────────────────────
    def _build_step3(self):
        frame = self._step_content

        tk.Label(
            frame,
            text=f"Barbero: {self._sel_barber['nombre']}  |  "
                 f"Servicio: {self._sel_service['nombre']}  |  "
                 f"Duración: {self._sel_service['duracion_min']} min",
            font=FONTS["small"], bg=COLORS["bg_medium"], fg=COLORS["accent"]
        ).pack(anchor="w")
        tk.Label(frame, text="Elige Fecha y Hora",
                 font=FONTS["subtitle"], bg=COLORS["bg_medium"],
                 fg=COLORS["text_white"]).pack(anchor="w", pady=(0, PADDING["md"]))

        body = tk.Frame(frame, bg=COLORS["bg_medium"])
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        # Calendario
        cal_frame = tk.Frame(body, bg=COLORS["bg_card"],
                             padx=PADDING["md"], pady=PADDING["md"])
        cal_frame.grid(row=0, column=0, sticky="nsew", padx=(0, PADDING["md"]))

        self._cal_year  = datetime.now().year
        self._cal_month = datetime.now().month
        self._selected_date_btn = None

        self._cal_header = tk.Frame(cal_frame, bg=COLORS["bg_card"])
        self._cal_header.pack(fill="x")
        self._cal_grid   = tk.Frame(cal_frame, bg=COLORS["bg_card"])
        self._cal_grid.pack(fill="both", expand=True)

        self._render_calendar()

        # Slots
        slots_frame = tk.Frame(body, bg=COLORS["bg_card"],
                               padx=PADDING["md"], pady=PADDING["md"])
        slots_frame.grid(row=0, column=1, sticky="nsew")

        tk.Label(slots_frame, text="Horarios disponibles",
                 font=FONTS["body_bold"], bg=COLORS["bg_card"],
                 fg=COLORS["text_white"]).pack(anchor="w", pady=(0, PADDING["sm"]))

        self._slots_var = tk.StringVar()
        self._slots_listbox_frame = tk.Frame(slots_frame, bg=COLORS["bg_card"])
        self._slots_listbox_frame.pack(fill="both", expand=True)

        tk.Label(
            self._slots_listbox_frame,
            text="← Selecciona una fecha",
            font=FONTS["body"], bg=COLORS["bg_card"],
            fg=COLORS["text_muted"]
        ).pack(pady=PADDING["xl"])

        btn_row = tk.Frame(frame, bg=COLORS["bg_medium"])
        btn_row.pack(fill="x", pady=PADDING["md"])
        ModernButton(btn_row, text="← Atrás",
                     command=lambda: self._show_step(2), style="ghost").pack(side="left")
        self._next3_btn = ModernButton(btn_row, text="Siguiente →",
                                       command=self._confirm_slot, style="primary")
        self._next3_btn.pack(side="right")

    def _render_calendar(self):
        for w in self._cal_header.winfo_children():
            w.destroy()
        for w in self._cal_grid.winfo_children():
            w.destroy()

        month_name = ["", "Enero","Febrero","Marzo","Abril","Mayo","Junio",
                       "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

        nav = tk.Frame(self._cal_header, bg=COLORS["bg_card"])
        nav.pack(fill="x")

        tk.Button(
            nav, text="◀", font=FONTS["body"],
            bg=COLORS["bg_card"], fg=COLORS["text_white"],
            relief="flat", cursor="hand2",
            command=self._prev_month
        ).pack(side="left")

        tk.Label(
            nav,
            text=f"{month_name[self._cal_month]} {self._cal_year}",
            font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_white"]
        ).pack(side="left", expand=True)

        tk.Button(
            nav, text="▶", font=FONTS["body"],
            bg=COLORS["bg_card"], fg=COLORS["text_white"],
            relief="flat", cursor="hand2",
            command=self._next_month
        ).pack(side="right")

        # Días de la semana
        for i, d in enumerate(["Lu","Ma","Mi","Ju","Vi","Sá","Do"]):
            tk.Label(
                self._cal_grid, text=d, font=FONTS["small"],
                bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                width=4
            ).grid(row=0, column=i, padx=1, pady=1)

        # Días del mes
        today = date.today()
        cal_matrix = calendar.monthcalendar(self._cal_year, self._cal_month)

        for r, week in enumerate(cal_matrix):
            for c, day in enumerate(week):
                if day == 0:
                    tk.Label(self._cal_grid, text="", width=4,
                             bg=COLORS["bg_card"]).grid(row=r+1, column=c)
                    continue

                d = date(self._cal_year, self._cal_month, day)
                is_past = d < today

                day_btn = tk.Button(
                    self._cal_grid, text=str(day), width=4,
                    font=FONTS["small"],
                    bg=COLORS["bg_card"] if not is_past else COLORS["bg_dark"],
                    fg=COLORS["text_muted"] if is_past else COLORS["text_white"],
                    relief="flat", cursor="arrow" if is_past else "hand2",
                    state="disabled" if is_past else "normal",
                    command=lambda d_=d: self._select_date(d_)
                )
                if d == today:
                    day_btn.config(fg=COLORS["accent"], font=FONTS["body_bold"])

                day_btn.grid(row=r+1, column=c, padx=1, pady=1)

    def _prev_month(self):
        if self._cal_month == 1:
            self._cal_month = 12
            self._cal_year -= 1
        else:
            self._cal_month -= 1
        self._render_calendar()

    def _next_month(self):
        if self._cal_month == 12:
            self._cal_month = 1
            self._cal_year += 1
        else:
            self._cal_month += 1
        self._render_calendar()

    def _select_date(self, d: date):
        self._sel_date = d.strftime("%Y-%m-%d")
        self._render_slots()

    def _render_slots(self):
        for w in self._slots_listbox_frame.winfo_children():
            w.destroy()

        slots = db.get_available_slots(
            self._sel_barber["id"],
            self._sel_date,
            int(self._sel_service["duracion_min"])
        )

        tk.Label(
            self._slots_listbox_frame,
            text=f"Fecha: {self._sel_date}",
            font=FONTS["body_bold"], bg=COLORS["bg_card"],
            fg=COLORS["text_white"]
        ).pack(anchor="w", pady=(0, PADDING["sm"]))

        if not slots:
            tk.Label(
                self._slots_listbox_frame,
                text="No hay horarios disponibles\npara esta fecha.",
                font=FONTS["body"], bg=COLORS["bg_card"],
                fg=COLORS["text_muted"]
            ).pack(pady=PADDING["xl"])
            return

        canvas_frame = tk.Frame(self._slots_listbox_frame, bg=COLORS["bg_card"])
        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg=COLORS["bg_card"],
                           highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical",
                                   command=canvas.yview)
        slots_inner = tk.Frame(canvas, bg=COLORS["bg_card"])

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=slots_inner, anchor="nw")
        slots_inner.bind("<Configure>",
                         lambda e: canvas.configure(
                             scrollregion=canvas.bbox("all")))

        self._slot_buttons = {}
        self._selected_slot = None

        cols = 4
        for i, slot in enumerate(slots):
            btn = tk.Button(
                slots_inner, text=slot, font=FONTS["body"],
                bg=COLORS["bg_light"], fg=COLORS["text_white"],
                relief="flat", cursor="hand2", width=6,
                command=lambda s=slot: self._pick_slot(s)
            )
            btn.grid(row=i // cols, column=i % cols, padx=4, pady=4)
            self._slot_buttons[slot] = btn

    def _pick_slot(self, slot: str):
        # Resetear todos los botones
        for s, btn in self._slot_buttons.items():
            btn.config(bg=COLORS["bg_light"], fg=COLORS["text_white"])
        # Resaltar el seleccionado
        self._slot_buttons[slot].config(
            bg=COLORS["accent_green"], fg=COLORS["text_white"])
        self._selected_slot = slot

    def _confirm_slot(self):
        if not self._sel_date:
            messagebox.showinfo("Sin fecha", "Selecciona una fecha.")
            return
        if not hasattr(self, "_selected_slot") or not self._selected_slot:
            messagebox.showinfo("Sin hora", "Selecciona un horario.")
            return
        self._sel_slot = self._selected_slot
        self._show_step(4)

    # ── Paso 4: Confirmar ─────────────────────────────────────────────────────
    def _build_step4(self):
        frame = self._step_content

        tk.Label(frame, text="Confirmar Reserva",
                 font=FONTS["subtitle"], bg=COLORS["bg_medium"],
                 fg=COLORS["text_white"]).pack(anchor="w", pady=(0, PADDING["md"]))

        # Calcular hora de fin
        from datetime import datetime, timedelta
        start = datetime.strptime(
            f"{self._sel_date} {self._sel_slot}", "%Y-%m-%d %H:%M")
        end   = start + timedelta(minutes=int(self._sel_service["duracion_min"]))
        hora_fin = end.strftime("%H:%M")

        card = tk.Frame(frame, bg=COLORS["bg_card"],
                        padx=PADDING["xl"], pady=PADDING["xl"])
        card.pack(pady=PADDING["md"])

        tk.Label(card, text="📋 Resumen de tu Cita",
                 font=FONTS["subtitle"], bg=COLORS["bg_card"],
                 fg=COLORS["accent"]).pack(pady=(0, PADDING["md"]))

        details = [
            ("💈 Barbero",   self._sel_barber["nombre"]),
            ("✂️  Servicio",  self._sel_service["nombre"]),
            ("💰 Precio",    f"${self._sel_service['precio']:,.0f}"),
            ("📆 Fecha",     self._sel_date),
            ("🕐 Hora inicio", self._sel_slot),
            ("🕑 Hora fin",    hora_fin),
            ("⏱ Duración",   f"{self._sel_service['duracion_min']} min"),
        ]

        for label, value in details:
            row = tk.Frame(card, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=FONTS["body_bold"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                     width=16, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=FONTS["body"],
                     bg=COLORS["bg_card"], fg=COLORS["text_white"]).pack(side="left")

        btn_row = tk.Frame(frame, bg=COLORS["bg_medium"])
        btn_row.pack(fill="x", pady=PADDING["md"])
        ModernButton(btn_row, text="← Atrás",
                     command=lambda: self._show_step(3), style="ghost").pack(side="left")
        ModernButton(btn_row, text="✅ Confirmar Reserva",
                     command=lambda hf=hora_fin: self._book(hf),
                     style="success").pack(side="right")

    def _book(self, hora_fin: str):
        if not messagebox.askyesno(
            "Confirmar reserva",
            f"¿Confirmas tu cita con {self._sel_barber['nombre']} "
            f"el {self._sel_date} a las {self._sel_slot}?"
        ):
            return

        cid = db.create_appointment(
            cliente_id=self.user["id"],
            cliente_nombre=self.user["nombre"],
            barbero_id=int(self._sel_barber["id"]),
            barbero_nombre=self._sel_barber["nombre"],
            servicio_id=int(self._sel_service["id"]),
            servicio_nombre=self._sel_service["nombre"],
            precio=self._sel_service["precio"],
            fecha=self._sel_date,
            hora_inicio=self._sel_slot,
            hora_fin=hora_fin,
        )

        messagebox.showinfo(
            "✅ ¡Reserva confirmada!",
            f"Tu cita ha sido reservada exitosamente.\n"
            f"ID de cita: #{cid}\n\n"
            f"Barbero: {self._sel_barber['nombre']}\n"
            f"Fecha: {self._sel_date}  Hora: {self._sel_slot}"
        )

        # Resetear wizard
        self._sel_barber  = None
        self._sel_service = None
        self._sel_date    = None
        self._sel_slot    = None
        self._show_step(1)


# ══════════════════════════════════════════════════════════════════════════════
class MisCitasPanel(tk.Frame):
    """Lista de citas del cliente con opciones de cancelar y reprogramar."""

    def __init__(self, parent, user):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self.user = user
        self._build()
        self._load_table()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["bg_medium"])
        header.pack(fill="x", padx=PADDING["lg"], pady=(PADDING["lg"], 0))

        tk.Label(
            header, text="📋  Mis Citas",
            font=FONTS["title"], bg=COLORS["bg_medium"], fg=COLORS["text_white"]
        ).pack(side="left")

        Divider(self).pack(fill="x", padx=PADDING["lg"], pady=PADDING["sm"])

        # Filtro estado
        filt = tk.Frame(self, bg=COLORS["bg_medium"])
        filt.pack(fill="x", padx=PADDING["lg"])
        tk.Label(filt, text="Estado:", font=FONTS["small"],
                 bg=COLORS["bg_medium"], fg=COLORS["text_secondary"]).pack(side="left")
        self.f_estado = ttk.Combobox(
            filt, values=["Todas"] + APPOINTMENT_STATES,
            state="readonly", width=14, font=FONTS["small"]
        )
        self.f_estado.set("Todas")
        self.f_estado.pack(side="left", padx=4)
        ModernButton(filt, text="Filtrar",
                     command=self._load_table, style="info").pack(side="left", padx=4)

        # Tabla
        table_frame = tk.Frame(self, bg=COLORS["bg_medium"])
        table_frame.pack(fill="both", expand=True,
                         padx=PADDING["lg"], pady=PADDING["sm"])

        cols = [
            ("id",       "ID",       45),
            ("fecha",    "Fecha",   100),
            ("hora",     "Hora",     70),
            ("barbero",  "Barbero", 150),
            ("servicio", "Servicio",160),
            ("precio",   "Precio",   80),
            ("estado",   "Estado",  110),
        ]
        self.tree = ScrollableTreeview(table_frame, cols, height=14)
        self.tree.pack(fill="both", expand=True)
        self.tree.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Acciones
        actions = tk.Frame(self, bg=COLORS["bg_medium"])
        actions.pack(fill="x", padx=PADDING["lg"], pady=PADDING["sm"])

        ModernButton(actions, text="❌ Cancelar Cita",
                     command=self._cancel, style="danger").pack(side="left", padx=4)

    def _load_table(self):
        self.tree.clear()
        df = db.get_appointments_by_client(self.user["id"])
        if df.empty:
            return

        estado = self.f_estado.get()
        if estado != "Todas":
            df = df[df["estado"] == estado]

        for _, row in df.sort_values("fecha", ascending=False).iterrows():
            tag = row["estado"].lower().replace(" ", "_")
            self.tree.insert(
                (row["id"], row["fecha"], row["hora_inicio"],
                 row["barbero_nombre"], row["servicio_nombre"],
                 f"${row['precio']:,.0f}", row["estado"]),
                tags=(tag,)
            )
            color = STATE_COLORS.get(row["estado"], COLORS["text_primary"])
            self.tree.tag_configure(tag, foreground=color)

    def _on_select(self, _event=None):
        sel = self.tree.get_selected()
        self._sel_id = int(sel[0]) if sel else None

    def _cancel(self):
        if not hasattr(self, "_sel_id") or not self._sel_id:
            messagebox.showinfo("Sin selección", "Selecciona una cita para cancelar.")
            return
        if not messagebox.askyesno(
            "Cancelar cita",
            "¿Confirmas que deseas cancelar esta cita?"
        ):
            return
        db.cancel_appointment(self._sel_id)
        messagebox.showinfo("✅ Cancelada", "Tu cita ha sido cancelada.")
        self._load_table()


# ══════════════════════════════════════════════════════════════════════════════
class PerfilPanel(tk.Frame):
    """Información de perfil del cliente."""

    def __init__(self, parent, user):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self.user = user
        self._build()

    def _build(self):
        tk.Label(
            self, text="👤  Mi Perfil",
            font=FONTS["title"], bg=COLORS["bg_medium"], fg=COLORS["text_white"]
        ).pack(anchor="w", padx=PADDING["lg"], pady=(PADDING["lg"], 0))

        Divider(self).pack(fill="x", padx=PADDING["lg"], pady=PADDING["md"])

        card = tk.Frame(self, bg=COLORS["bg_card"],
                        padx=PADDING["xl"], pady=PADDING["xl"])
        card.pack(padx=PADDING["lg"])

        tk.Label(card, text="👤", font=("Segoe UI", 48),
                 bg=COLORS["bg_card"], fg=COLORS["accent_green"]).pack()
        tk.Label(card, text=self.user["nombre"], font=FONTS["subtitle"],
                 bg=COLORS["bg_card"], fg=COLORS["text_white"]).pack()

        Divider(card).pack(fill="x", pady=PADDING["md"])

        fields = [
            ("📧 Email",     self.user["email"]),
            ("📞 Teléfono",  self.user["telefono"]),
            ("🔖 Rol",       self.user["rol"].capitalize()),
            ("📅 Registro",  str(self.user["fecha_registro"])[:10]),
        ]
        for label, value in fields:
            row = tk.Frame(card, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=FONTS["body_bold"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                     width=14, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=FONTS["body"],
                     bg=COLORS["bg_card"], fg=COLORS["text_white"]).pack(side="left")
