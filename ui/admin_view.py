"""
admin_view.py - Panel de Administración
CRUD de barberos, servicios y gestión completa de citas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from core.styles import COLORS, FONTS, PADDING, SERVICE_CATEGORIES, APPOINTMENT_STATES, WORK_HOURS
from core import database as db
from ui.widgets import (ModernButton, LabeledEntry, LabeledCombo,
                         ScrollableTreeview, Card, Divider, TitleLabel,
                         SubtitleLabel, STATE_COLORS)


# ══════════════════════════════════════════════════════════════════════════════
class AdminView(tk.Frame):
    """Panel principal del administrador con sidebar de navegación."""

    SECTIONS = [
        ("📊", "Dashboard",   "dashboard"),
        ("💈", "Barberos",    "barberos"),
        ("✂️",  "Servicios",   "servicios"),
        ("📅", "Citas",       "citas"),
        ("👥", "Clientes",    "clientes"),
    ]

    def __init__(self, parent, user: dict, on_logout):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.user = user
        self.on_logout = on_logout
        self._active_section = "dashboard"
        self._build()

    # ── Estructura principal ─────────────────────────────────────────────────
    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._content = tk.Frame(self, bg=COLORS["bg_medium"])
        self._content.grid(row=0, column=1, sticky="nsew")
        self._navigate("dashboard")

    def _build_sidebar(self):
        sb = tk.Frame(self, bg=COLORS["sidebar_bg"],
                      width=PADDING["xl"] * 5)
        sb.grid(row=0, column=0, sticky="ns")
        sb.grid_propagate(False)

        # Logo
        tk.Label(
            sb, text="✂", font=("Segoe UI", 32),
            bg=COLORS["sidebar_bg"], fg=COLORS["accent"]
        ).pack(pady=(PADDING["lg"], 0))
        tk.Label(
            sb, text="BARBERÍA PRO",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["sidebar_bg"], fg=COLORS["text_white"]
        ).pack()
        tk.Label(
            sb, text="Administrador",
            font=FONTS["small"],
            bg=COLORS["sidebar_bg"], fg=COLORS["text_muted"]
        ).pack(pady=(0, PADDING["md"]))

        Divider(sb).pack(fill="x", padx=PADDING["sm"])

        # Botones de navegación
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

        # Logout en la parte inferior
        tk.Frame(sb, bg=COLORS["sidebar_bg"]).pack(expand=True)
        Divider(sb).pack(fill="x", padx=PADDING["sm"])
        ModernButton(
            sb, text="  🚪 Cerrar Sesión",
            command=self.on_logout, style="danger"
        ).pack(fill="x", pady=PADDING["sm"], padx=PADDING["sm"])

    # ── Navegación ────────────────────────────────────────────────────────────
    def _navigate(self, section: str):
        # Actualizar estado visual de los botones
        for key, btn in self._nav_buttons.items():
            if key == section:
                btn.config(bg=COLORS["accent"], fg=COLORS["text_white"])
            else:
                btn.config(bg=COLORS["sidebar_bg"], fg=COLORS["text_secondary"])

        self._active_section = section
        for w in self._content.winfo_children():
            w.destroy()

        sections_map = {
            "dashboard": DashboardPanel,
            "barberos":  BarberosPanel,
            "servicios": ServiciosPanel,
            "citas":     CitasPanel,
            "clientes":  ClientesPanel,
        }
        cls = sections_map.get(section, DashboardPanel)
        cls(self._content).pack(fill="both", expand=True)


# ══════════════════════════════════════════════════════════════════════════════
class DashboardPanel(tk.Frame):
    """Estadísticas generales del negocio."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self._build()

    def _build(self):
        tk.Label(
            self, text="📊  Dashboard",
            font=FONTS["title"], bg=COLORS["bg_medium"], fg=COLORS["text_white"]
        ).pack(anchor="w", padx=PADDING["lg"], pady=(PADDING["lg"], PADDING["md"]))

        Divider(self).pack(fill="x", padx=PADDING["lg"])

        # Tarjetas de estadísticas
        stats_frame = tk.Frame(self, bg=COLORS["bg_medium"])
        stats_frame.pack(fill="x", padx=PADDING["lg"], pady=PADDING["md"])

        citas_df   = db.get_all_appointments()
        total      = len(citas_df)
        pendientes = len(citas_df[citas_df["estado"] == "Pendiente"]) if not citas_df.empty else 0
        hoy        = datetime.now().strftime("%Y-%m-%d")
        hoy_count  = len(citas_df[citas_df["fecha"] == hoy]) if not citas_df.empty else 0
        barberos   = len(db.get_all_barbers(only_active=True))

        cards_data = [
            ("📅", "Total Citas",       str(total),      COLORS["accent_blue"]),
            ("⏳", "Pendientes",        str(pendientes),  COLORS["accent_orange"]),
            ("📆", "Citas Hoy",         str(hoy_count),   COLORS["accent_green"]),
            ("💈", "Barberos Activos",  str(barberos),    COLORS["accent"]),
        ]

        for i, (icon, label, value, color) in enumerate(cards_data):
            c = tk.Frame(stats_frame, bg=COLORS["bg_card"],
                         padx=PADDING["lg"], pady=PADDING["lg"])
            c.grid(row=0, column=i, padx=8, pady=8, sticky="ew")
            stats_frame.grid_columnconfigure(i, weight=1)

            tk.Label(c, text=icon, font=("Segoe UI", 28),
                     bg=COLORS["bg_card"], fg=color).pack()
            tk.Label(c, text=value, font=("Segoe UI", 22, "bold"),
                     bg=COLORS["bg_card"], fg=color).pack()
            tk.Label(c, text=label, font=FONTS["small"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack()

        # Últimas citas
        tk.Label(
            self, text="Últimas 10 Citas",
            font=FONTS["subtitle"], bg=COLORS["bg_medium"], fg=COLORS["text_white"]
        ).pack(anchor="w", padx=PADDING["lg"], pady=(PADDING["md"], PADDING["sm"]))

        cols = [
            ("id",       "ID",       50),
            ("fecha",    "Fecha",   100),
            ("hora",     "Hora",     70),
            ("cliente",  "Cliente", 160),
            ("barbero",  "Barbero", 160),
            ("servicio", "Servicio",160),
            ("estado",   "Estado",  110),
        ]
        tree_frame = tk.Frame(self, bg=COLORS["bg_medium"])
        tree_frame.pack(fill="both", expand=True,
                        padx=PADDING["lg"], pady=(0, PADDING["lg"]))
        self.tree = ScrollableTreeview(tree_frame, cols, height=10)
        self.tree.pack(fill="both", expand=True)

        if not citas_df.empty:
            recent = citas_df.sort_values("fecha_creacion",
                                          ascending=False).head(10)
            for _, row in recent.iterrows():
                tag = row["estado"].lower().replace(" ", "_")
                self.tree.insert(
                    (row["id"], row["fecha"], row["hora_inicio"],
                     row["cliente_nombre"], row["barbero_nombre"],
                     row["servicio_nombre"], row["estado"]),
                    tags=(tag,)
                )
                color = STATE_COLORS.get(row["estado"], COLORS["text_primary"])
                self.tree.tag_configure(tag, foreground=color)


# ══════════════════════════════════════════════════════════════════════════════
class BarberosPanel(tk.Frame):
    """CRUD completo de barberos."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self._selected_id = None
        self._build()
        self._load_table()

    def _build(self):
        # Cabecera
        header = tk.Frame(self, bg=COLORS["bg_medium"])
        header.pack(fill="x", padx=PADDING["lg"], pady=(PADDING["lg"], 0))

        tk.Label(
            header, text="💈  Gestión de Barberos",
            font=FONTS["title"], bg=COLORS["bg_medium"], fg=COLORS["text_white"]
        ).pack(side="left")

        ModernButton(
            header, text="+ Nuevo Barbero",
            command=self._clear_form, style="success"
        ).pack(side="right")

        Divider(self).pack(fill="x", padx=PADDING["lg"], pady=PADDING["sm"])

        # Layout: tabla izquierda, formulario derecha
        body = tk.Frame(self, bg=COLORS["bg_medium"])
        body.pack(fill="both", expand=True, padx=PADDING["lg"], pady=PADDING["sm"])
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        # ── Tabla ────────────────────────────────────────────────────────────
        left = tk.Frame(body, bg=COLORS["bg_medium"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, PADDING["md"]))

        # Buscador
        search_frame = tk.Frame(left, bg=COLORS["bg_medium"])
        search_frame.pack(fill="x", pady=(0, PADDING["sm"]))
        tk.Label(search_frame, text="🔍", font=FONTS["body"],
                 bg=COLORS["bg_medium"], fg=COLORS["text_secondary"]).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self._filter_table())
        tk.Entry(
            search_frame, textvariable=self.search_var,
            font=FONTS["body"], bg=COLORS["bg_input"],
            fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground=COLORS["bg_light"],
        ).pack(side="left", fill="x", expand=True, ipady=5, padx=4)

        cols = [
            ("id",          "ID",           40),
            ("nombre",      "Nombre",      150),
            ("especialidad","Especialidad",150),
            ("hora_inicio", "Inicio",       60),
            ("hora_fin",    "Fin",          60),
            ("activo",      "Estado",       80),
        ]
        self.tree = ScrollableTreeview(left, cols, height=14)
        self.tree.pack(fill="both", expand=True)
        self.tree.tree.bind("<<TreeviewSelect>>", self._on_select)

        # ── Formulario ───────────────────────────────────────────────────────
        right = tk.Frame(body, bg=COLORS["bg_card"],
                         padx=PADDING["md"], pady=PADDING["md"])
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            right, text="Datos del Barbero",
            font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["accent"]
        ).pack(anchor="w", pady=(0, PADDING["sm"]))

        self.f_nombre      = LabeledEntry(right, label="Nombre completo")
        self.f_nombre.configure(bg=COLORS["bg_card"])
        self.f_nombre.pack(fill="x", pady=4)

        self.f_especialidad = LabeledEntry(right, label="Especialidad")
        self.f_especialidad.configure(bg=COLORS["bg_card"])
        self.f_especialidad.pack(fill="x", pady=4)

        tk.Label(right, text="Horario de trabajo",
                 font=FONTS["small"], bg=COLORS["bg_card"],
                 fg=COLORS["text_secondary"]).pack(anchor="w")

        hrs_frame = tk.Frame(right, bg=COLORS["bg_card"])
        hrs_frame.pack(fill="x", pady=4)

        self.f_inicio = ttk.Combobox(hrs_frame, values=WORK_HOURS,
                                      state="readonly", width=8,
                                      font=FONTS["small"])
        self.f_inicio.pack(side="left", padx=(0, 4))

        tk.Label(hrs_frame, text="a", font=FONTS["body"],
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(side="left")

        self.f_fin = ttk.Combobox(hrs_frame, values=WORK_HOURS,
                                   state="readonly", width=8,
                                   font=FONTS["small"])
        self.f_fin.pack(side="left", padx=(4, 0))

        self.f_activo_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            right, text="Activo",
            variable=self.f_activo_var,
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_input"],
            font=FONTS["body"], activebackground=COLORS["bg_card"],
        ).pack(anchor="w", pady=PADDING["sm"])

        # Botones del formulario
        btn_frame = tk.Frame(right, bg=COLORS["bg_card"])
        btn_frame.pack(fill="x", pady=PADDING["sm"])

        ModernButton(btn_frame, text="💾 Guardar",
                     command=self._save, style="primary").pack(
            side="left", padx=(0, 4))
        ModernButton(btn_frame, text="🗑 Eliminar",
                     command=self._delete, style="danger").pack(side="left", padx=4)
        ModernButton(btn_frame, text="✖ Limpiar",
                     command=self._clear_form, style="ghost").pack(side="left", padx=4)

    # ── Métodos ───────────────────────────────────────────────────────────────
    def _load_table(self):
        self.tree.clear()
        self._all_rows = []
        for _, row in db.get_all_barbers().iterrows():
            values = (
                row["id"], row["nombre"], row["especialidad"],
                row["hora_inicio"], row["hora_fin"],
                "✅ Activo" if row["activo"] else "❌ Inactivo"
            )
            self._all_rows.append(values)
            self.tree.insert(values)

    def _filter_table(self):
        term = self.search_var.get().lower()
        self.tree.clear()
        for row in self._all_rows:
            if term in str(row).lower():
                self.tree.insert(row)

    def _on_select(self, _event=None):
        sel = self.tree.get_selected()
        if not sel:
            return
        bid = int(sel[0])
        barber = db.get_barber_by_id(bid)
        if not barber:
            return
        self._selected_id = bid
        self.f_nombre.set(barber["nombre"])
        self.f_especialidad.set(barber["especialidad"])
        self.f_inicio.set(str(barber["hora_inicio"]))
        self.f_fin.set(str(barber["hora_fin"]))
        self.f_activo_var.set(bool(barber["activo"]))

    def _save(self):
        nombre  = self.f_nombre.get().strip()
        espec   = self.f_especialidad.get().strip()
        inicio  = self.f_inicio.get()
        fin     = self.f_fin.get()
        activo  = self.f_activo_var.get()

        if not all([nombre, espec, inicio, fin]):
            messagebox.showwarning("Campos requeridos",
                                   "Completa todos los campos.")
            return
        if inicio >= fin:
            messagebox.showwarning("Horario inválido",
                                   "La hora de inicio debe ser antes de la hora de fin.")
            return

        if self._selected_id:
            db.update_barber(self._selected_id, nombre=nombre,
                             especialidad=espec, hora_inicio=inicio,
                             hora_fin=fin, activo=activo)
            messagebox.showinfo("✅ Actualizado",
                                f"Barbero '{nombre}' actualizado.")
        else:
            db.create_barber(nombre, espec, inicio, fin)
            messagebox.showinfo("✅ Creado",
                                f"Barbero '{nombre}' creado.")

        self._clear_form()
        self._load_table()

    def _delete(self):
        if not self._selected_id:
            messagebox.showinfo("Sin selección",
                                "Selecciona un barbero de la tabla.")
            return
        barber = db.get_barber_by_id(self._selected_id)
        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar al barbero '{barber['nombre']}'?\nEsta acción no se puede deshacer."
        ):
            return
        db.delete_barber(self._selected_id)
        messagebox.showinfo("✅ Eliminado", "Barbero eliminado correctamente.")
        self._clear_form()
        self._load_table()

    def _clear_form(self):
        self._selected_id = None
        self.f_nombre.clear()
        self.f_especialidad.clear()
        self.f_inicio.set("")
        self.f_fin.set("")
        self.f_activo_var.set(True)


# ══════════════════════════════════════════════════════════════════════════════
class ServiciosPanel(tk.Frame):
    """CRUD completo de servicios."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self._selected_id = None
        self._build()
        self._load_table()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["bg_medium"])
        header.pack(fill="x", padx=PADDING["lg"], pady=(PADDING["lg"], 0))

        tk.Label(
            header, text="✂️  Gestión de Servicios",
            font=FONTS["title"], bg=COLORS["bg_medium"], fg=COLORS["text_white"]
        ).pack(side="left")
        ModernButton(
            header, text="+ Nuevo Servicio",
            command=self._clear_form, style="success"
        ).pack(side="right")

        Divider(self).pack(fill="x", padx=PADDING["lg"], pady=PADDING["sm"])

        body = tk.Frame(self, bg=COLORS["bg_medium"])
        body.pack(fill="both", expand=True, padx=PADDING["lg"])
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        # ── Tabla ────────────────────────────────────────────────────────────
        left = tk.Frame(body, bg=COLORS["bg_medium"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, PADDING["md"]))

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self._filter_table())
        srch = tk.Frame(left, bg=COLORS["bg_medium"])
        srch.pack(fill="x", pady=(0, PADDING["sm"]))
        tk.Label(srch, text="🔍", font=FONTS["body"],
                 bg=COLORS["bg_medium"], fg=COLORS["text_secondary"]).pack(side="left")
        tk.Entry(
            srch, textvariable=self.search_var,
            font=FONTS["body"], bg=COLORS["bg_input"],
            fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground=COLORS["bg_light"],
        ).pack(side="left", fill="x", expand=True, ipady=5, padx=4)

        cols = [
            ("id",       "ID",         40),
            ("nombre",   "Servicio",  180),
            ("precio",   "Precio",     80),
            ("duracion", "Duración",   80),
            ("categoria","Categoría", 100),
            ("activo",   "Estado",     80),
        ]
        self.tree = ScrollableTreeview(left, cols, height=14)
        self.tree.pack(fill="both", expand=True)
        self.tree.tree.bind("<<TreeviewSelect>>", self._on_select)

        # ── Formulario ───────────────────────────────────────────────────────
        right = tk.Frame(body, bg=COLORS["bg_card"],
                         padx=PADDING["md"], pady=PADDING["md"])
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            right, text="Datos del Servicio",
            font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["accent"]
        ).pack(anchor="w", pady=(0, PADDING["sm"]))

        self.f_nombre = LabeledEntry(right, label="Nombre del servicio")
        self.f_nombre.configure(bg=COLORS["bg_card"])
        self.f_nombre.pack(fill="x", pady=4)

        self.f_precio = LabeledEntry(right, label="Precio ($)")
        self.f_precio.configure(bg=COLORS["bg_card"])
        self.f_precio.pack(fill="x", pady=4)

        self.f_duracion = LabeledEntry(right, label="Duración (minutos)")
        self.f_duracion.configure(bg=COLORS["bg_card"])
        self.f_duracion.pack(fill="x", pady=4)

        tk.Label(right, text="Categoría", font=FONTS["small"],
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.f_categoria = ttk.Combobox(
            right, values=SERVICE_CATEGORIES, state="readonly",
            font=FONTS["body"]
        )
        self.f_categoria.pack(fill="x", ipady=4, pady=(0, 4))

        self.f_activo_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            right, text="Activo",
            variable=self.f_activo_var,
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_input"], font=FONTS["body"],
            activebackground=COLORS["bg_card"],
        ).pack(anchor="w", pady=PADDING["sm"])

        btn_frame = tk.Frame(right, bg=COLORS["bg_card"])
        btn_frame.pack(fill="x", pady=PADDING["sm"])
        ModernButton(btn_frame, text="💾 Guardar",
                     command=self._save, style="primary").pack(side="left", padx=(0, 4))
        ModernButton(btn_frame, text="🗑 Eliminar",
                     command=self._delete, style="danger").pack(side="left", padx=4)
        ModernButton(btn_frame, text="✖ Limpiar",
                     command=self._clear_form, style="ghost").pack(side="left", padx=4)

    def _load_table(self):
        self.tree.clear()
        self._all_rows = []
        for _, row in db.get_all_services().iterrows():
            v = (
                row["id"], row["nombre"],
                f"${row['precio']:,.0f}", f"{row['duracion_min']} min",
                row["categoria"],
                "✅ Activo" if row["activo"] else "❌ Inactivo"
            )
            self._all_rows.append(v)
            self.tree.insert(v)

    def _filter_table(self):
        term = self.search_var.get().lower()
        self.tree.clear()
        for row in self._all_rows:
            if term in str(row).lower():
                self.tree.insert(row)

    def _on_select(self, _event=None):
        sel = self.tree.get_selected()
        if not sel:
            return
        sid = int(sel[0])
        svc = db.get_service_by_id(sid)
        if not svc:
            return
        self._selected_id = sid
        self.f_nombre.set(svc["nombre"])
        self.f_precio.set(str(svc["precio"]))
        self.f_duracion.set(str(svc["duracion_min"]))
        self.f_categoria.set(svc["categoria"])
        self.f_activo_var.set(bool(svc["activo"]))

    def _save(self):
        nombre   = self.f_nombre.get().strip()
        precio   = self.f_precio.get().strip()
        duracion = self.f_duracion.get().strip()
        categoria = self.f_categoria.get()
        activo   = self.f_activo_var.get()

        if not all([nombre, precio, duracion, categoria]):
            messagebox.showwarning("Campos requeridos", "Completa todos los campos.")
            return
        try:
            precio   = float(precio)
            duracion = int(duracion)
        except ValueError:
            messagebox.showwarning("Datos inválidos",
                                   "Precio y duración deben ser números.")
            return

        if self._selected_id:
            db.update_service(self._selected_id, nombre=nombre, precio=precio,
                              duracion_min=duracion, categoria=categoria, activo=activo)
            messagebox.showinfo("✅ Actualizado", f"Servicio '{nombre}' actualizado.")
        else:
            db.create_service(nombre, precio, duracion, categoria)
            messagebox.showinfo("✅ Creado", f"Servicio '{nombre}' creado.")

        self._clear_form()
        self._load_table()

    def _delete(self):
        if not self._selected_id:
            messagebox.showinfo("Sin selección", "Selecciona un servicio de la tabla.")
            return
        svc = db.get_service_by_id(self._selected_id)
        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar el servicio '{svc['nombre']}'?"
        ):
            return
        db.delete_service(self._selected_id)
        messagebox.showinfo("✅ Eliminado", "Servicio eliminado.")
        self._clear_form()
        self._load_table()

    def _clear_form(self):
        self._selected_id = None
        self.f_nombre.clear()
        self.f_precio.clear()
        self.f_duracion.clear()
        self.f_categoria.set("")
        self.f_activo_var.set(True)


# ══════════════════════════════════════════════════════════════════════════════
class CitasPanel(tk.Frame):
    """Gestión completa de citas con filtros."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self._build()
        self._load_table()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["bg_medium"])
        header.pack(fill="x", padx=PADDING["lg"], pady=(PADDING["lg"], 0))

        tk.Label(
            header, text="📅  Gestión de Citas",
            font=FONTS["title"], bg=COLORS["bg_medium"], fg=COLORS["text_white"]
        ).pack(side="left")

        Divider(self).pack(fill="x", padx=PADDING["lg"], pady=PADDING["sm"])

        # Filtros
        filt = tk.Frame(self, bg=COLORS["bg_card"],
                        padx=PADDING["md"], pady=PADDING["sm"])
        filt.pack(fill="x", padx=PADDING["lg"])

        tk.Label(filt, text="Filtrar:", font=FONTS["body_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["text_white"]).grid(
            row=0, column=0, padx=4)

        tk.Label(filt, text="Fecha:", font=FONTS["small"],
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
            row=0, column=1, padx=(8, 2))
        self.f_fecha = tk.Entry(filt, font=FONTS["body"], width=12,
                                bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                                insertbackground=COLORS["text_primary"],
                                relief="flat", bd=0)
        self.f_fecha.grid(row=0, column=2, ipady=4, padx=2)

        tk.Label(filt, text="Barbero:", font=FONTS["small"],
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
            row=0, column=3, padx=(8, 2))
        barbero_names = ["Todos"] + [
            row["nombre"] for _, row in db.get_all_barbers().iterrows()
        ]
        self.f_barbero = ttk.Combobox(filt, values=barbero_names,
                                       state="readonly", width=14,
                                       font=FONTS["small"])
        self.f_barbero.set("Todos")
        self.f_barbero.grid(row=0, column=4, padx=2)

        tk.Label(filt, text="Estado:", font=FONTS["small"],
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
            row=0, column=5, padx=(8, 2))
        self.f_estado = ttk.Combobox(
            filt, values=["Todos"] + APPOINTMENT_STATES,
            state="readonly", width=12, font=FONTS["small"]
        )
        self.f_estado.set("Todos")
        self.f_estado.grid(row=0, column=6, padx=2)

        ModernButton(filt, text="🔍 Filtrar",
                     command=self._load_table, style="info").grid(
            row=0, column=7, padx=8)
        ModernButton(filt, text="↺ Limpiar",
                     command=self._reset_filters, style="ghost").grid(
            row=0, column=8)

        # Tabla
        table_frame = tk.Frame(self, bg=COLORS["bg_medium"])
        table_frame.pack(fill="both", expand=True,
                         padx=PADDING["lg"], pady=PADDING["sm"])

        cols = [
            ("id",       "ID",       45),
            ("fecha",    "Fecha",   100),
            ("hora",     "Hora",     70),
            ("cliente",  "Cliente", 150),
            ("barbero",  "Barbero", 150),
            ("servicio", "Servicio",160),
            ("precio",   "Precio",   80),
            ("estado",   "Estado",  110),
        ]
        self.tree = ScrollableTreeview(table_frame, cols, height=16)
        self.tree.pack(fill="both", expand=True)
        self.tree.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Acciones
        actions = tk.Frame(self, bg=COLORS["bg_medium"])
        actions.pack(fill="x", padx=PADDING["lg"], pady=PADDING["sm"])

        for state in APPOINTMENT_STATES:
            style_map = {
                "Pendiente":  "warning",
                "Confirmada": "success",
                "Cancelada":  "danger",
                "Finalizada": "ghost",
            }
            ModernButton(
                actions, text=state,
                command=lambda s=state: self._change_state(s),
                style=style_map.get(state, "info")
            ).pack(side="left", padx=4)

    def _load_table(self):
        self.tree.clear()
        df = db.get_all_appointments()
        if df.empty:
            return

        fecha   = self.f_fecha.get().strip()
        barbero = self.f_barbero.get()
        estado  = self.f_estado.get()

        if fecha:
            df = df[df["fecha"].astype(str).str.contains(fecha)]
        if barbero != "Todos":
            df = df[df["barbero_nombre"] == barbero]
        if estado != "Todos":
            df = df[df["estado"] == estado]

        for _, row in df.sort_values("fecha", ascending=False).iterrows():
            tag = row["estado"].lower().replace(" ", "_")
            self.tree.insert(
                (row["id"], row["fecha"], row["hora_inicio"],
                 row["cliente_nombre"], row["barbero_nombre"],
                 row["servicio_nombre"], f"${row['precio']:,.0f}", row["estado"]),
                tags=(tag,)
            )
            color = STATE_COLORS.get(row["estado"], COLORS["text_primary"])
            self.tree.tag_configure(tag, foreground=color)

    def _reset_filters(self):
        self.f_fecha.delete(0, "end")
        self.f_barbero.set("Todos")
        self.f_estado.set("Todos")
        self._load_table()

    def _on_select(self, _event=None):
        sel = self.tree.get_selected()
        self._selected_id = int(sel[0]) if sel else None

    def _change_state(self, new_state: str):
        if not hasattr(self, "_selected_id") or not self._selected_id:
            messagebox.showinfo("Sin selección", "Selecciona una cita de la tabla.")
            return
        if not messagebox.askyesno(
            "Cambiar estado",
            f"¿Cambiar el estado de la cita a '{new_state}'?"
        ):
            return
        db.update_appointment(self._selected_id, estado=new_state)
        self._load_table()


# ══════════════════════════════════════════════════════════════════════════════
class ClientesPanel(tk.Frame):
    """Vista de solo lectura de clientes registrados."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self._build()
        self._load_table()

    def _build(self):
        tk.Label(
            self, text="👥  Clientes Registrados",
            font=FONTS["title"], bg=COLORS["bg_medium"], fg=COLORS["text_white"]
        ).pack(anchor="w", padx=PADDING["lg"], pady=(PADDING["lg"], PADDING["sm"]))

        Divider(self).pack(fill="x", padx=PADDING["lg"])

        table_frame = tk.Frame(self, bg=COLORS["bg_medium"])
        table_frame.pack(fill="both", expand=True,
                         padx=PADDING["lg"], pady=PADDING["md"])

        cols = [
            ("id",        "ID",          40),
            ("nombre",    "Nombre",     180),
            ("telefono",  "Teléfono",   130),
            ("email",     "Email",      200),
            ("fecha_reg", "Registro",   150),
        ]
        self.tree = ScrollableTreeview(table_frame, cols, height=18)
        self.tree.pack(fill="both", expand=True)

    def _load_table(self):
        self.tree.clear()
        df = db.get_all_users()
        clientes = df[df["rol"] == "cliente"]
        for _, row in clientes.iterrows():
            self.tree.insert((
                row["id"], row["nombre"], row["telefono"],
                row["email"], str(row["fecha_registro"])[:10]
            ))
