"""
database.py - Capa de acceso a datos usando Excel (.xlsx)
Gestiona todas las operaciones CRUD sobre el archivo de base de datos.
"""

import os
import sys
import logging
from datetime import datetime
import pandas as pd
from openpyxl import Workbook, load_workbook

logger = logging.getLogger(__name__)

# ── Ruta al archivo de base de datos ──────────────────────────────────────────
def get_db_path() -> str:
    """Devuelve la ruta del archivo .xlsx, compatible con PyInstaller."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "database.xlsx")


# ── Esquemas de columnas por hoja ─────────────────────────────────────────────
SCHEMAS = {
    "usuarios": [
        "id", "nombre", "telefono", "email", "password", "rol", "activo", "fecha_registro"
    ],
    "barberos": [
        "id", "nombre", "especialidad", "hora_inicio", "hora_fin", "activo", "fecha_registro"
    ],
    "servicios": [
        "id", "nombre", "precio", "duracion_min", "categoria", "activo", "fecha_registro"
    ],
    "citas": [
        "id", "cliente_id", "cliente_nombre", "barbero_id", "barbero_nombre",
        "servicio_id", "servicio_nombre", "precio", "fecha", "hora_inicio",
        "hora_fin", "estado", "notas", "fecha_creacion"
    ],
}


# ── Inicialización de la base de datos ────────────────────────────────────────
def init_database():
    """Crea el archivo Excel con hojas y datos iniciales si no existe."""
    path = get_db_path()
    if os.path.exists(path):
        logger.info("Base de datos existente encontrada en %s", path)
        return

    logger.info("Creando nueva base de datos en %s", path)
    wb = Workbook()
    wb.remove(wb.active)  # eliminar hoja por defecto

    for sheet, cols in SCHEMAS.items():
        ws = wb.create_sheet(sheet)
        ws.append(cols)

    wb.save(path)
    logger.info("Archivo creado. Insertando datos iniciales…")

    # Administrador por defecto
    _insert_row("usuarios", {
        "id": _next_id("usuarios"),
        "nombre": "Administrador",
        "telefono": "0000000000",
        "email": "admin@barberia.com",
        "password": "admin123",
        "rol": "admin",
        "activo": True,
        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })

    # Barberos de muestra
    for b in [
        ("Carlos Mendez", "Corte clásico", "08:00", "18:00"),
        ("Luis Torres",   "Barba y diseño", "09:00", "17:00"),
        ("Miguel Ríos",   "Coloración",      "08:00", "16:00"),
    ]:
        _insert_row("barberos", {
            "id": _next_id("barberos"),
            "nombre": b[0], "especialidad": b[1],
            "hora_inicio": b[2], "hora_fin": b[3],
            "activo": True,
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    # Servicios de muestra
    for s in [
        ("Corte clásico",     15000, 30,  "corte"),
        ("Corte moderno",     18000, 45,  "corte"),
        ("Arreglo de barba",  12000, 20,  "barba"),
        ("Barba completa",    20000, 40,  "barba"),
        ("Combo corte+barba", 30000, 60,  "combo"),
        ("Tinte completo",    45000, 90,  "coloración"),
        ("Mechas",            55000, 120, "coloración"),
    ]:
        _insert_row("servicios", {
            "id": _next_id("servicios"),
            "nombre": s[0], "precio": s[1],
            "duracion_min": s[2], "categoria": s[3],
            "activo": True,
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    logger.info("Datos iniciales insertados correctamente.")


# ── Helpers internos ──────────────────────────────────────────────────────────
def _load_df(sheet: str) -> pd.DataFrame:
    path = get_db_path()
    try:
        df = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
        # Forzar tipos coherentes
        for col in SCHEMAS[sheet]:
            if col not in df.columns:
                df[col] = None
        return df[SCHEMAS[sheet]]
    except Exception as e:
        logger.error("Error leyendo hoja '%s': %s", sheet, e)
        return pd.DataFrame(columns=SCHEMAS[sheet])


def _save_df(sheet: str, df: pd.DataFrame):
    path = get_db_path()
    try:
        wb = load_workbook(path)
        if sheet in wb.sheetnames:
            del wb[sheet]
        ws = wb.create_sheet(sheet)
        ws.append(list(df.columns))
        for row in df.itertuples(index=False):
            ws.append(list(row))
        wb.save(path)
    except Exception as e:
        logger.error("Error guardando hoja '%s': %s", sheet, e)
        raise


def _next_id(sheet: str) -> int:
    df = _load_df(sheet)
    if df.empty or df["id"].dropna().empty:
        return 1
    return int(df["id"].max()) + 1


def _insert_row(sheet: str, data: dict):
    df = _load_df(sheet)
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)
    _save_df(sheet, df)


# ── API pública ───────────────────────────────────────────────────────────────

# ---------- USUARIOS ----------------------------------------------------------
def get_all_users() -> pd.DataFrame:
    return _load_df("usuarios")

def get_user_by_email(email: str) -> dict | None:
    df = _load_df("usuarios")
    row = df[df["email"].str.lower() == email.lower()]
    return row.iloc[0].to_dict() if not row.empty else None

def get_user_by_id(uid: int) -> dict | None:
    df = _load_df("usuarios")
    row = df[df["id"] == uid]
    return row.iloc[0].to_dict() if not row.empty else None

def create_user(nombre, telefono, email, password) -> bool:
    if get_user_by_email(email):
        return False
    _insert_row("usuarios", {
        "id": _next_id("usuarios"),
        "nombre": nombre, "telefono": telefono,
        "email": email, "password": password,
        "rol": "cliente", "activo": True,
        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    logger.info("Usuario creado: %s", email)
    return True

def authenticate_user(email: str, password: str) -> dict | None:
    user = get_user_by_email(email)
    if user and str(user["password"]) == str(password) and user["activo"]:
        return user
    return None


# ---------- BARBEROS ----------------------------------------------------------
def get_all_barbers(only_active=False) -> pd.DataFrame:
    df = _load_df("barberos")
    if only_active:
        df = df[df["activo"] == True]
    return df

def get_barber_by_id(bid: int) -> dict | None:
    df = _load_df("barberos")
    row = df[df["id"] == bid]
    return row.iloc[0].to_dict() if not row.empty else None

def create_barber(nombre, especialidad, hora_inicio, hora_fin) -> int:
    nid = _next_id("barberos")
    _insert_row("barberos", {
        "id": nid, "nombre": nombre, "especialidad": especialidad,
        "hora_inicio": hora_inicio, "hora_fin": hora_fin,
        "activo": True,
        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    logger.info("Barbero creado: %s (id=%d)", nombre, nid)
    return nid

def update_barber(bid: int, **kwargs):
    df = _load_df("barberos")
    idx = df.index[df["id"] == bid]
    if idx.empty:
        return False
    for k, v in kwargs.items():
        if k in df.columns:
            df.at[idx[0], k] = v
    _save_df("barberos", df)
    logger.info("Barbero id=%d actualizado: %s", bid, kwargs)
    return True

def delete_barber(bid: int):
    df = _load_df("barberos")
    df = df[df["id"] != bid]
    _save_df("barberos", df)
    logger.info("Barbero id=%d eliminado", bid)


# ---------- SERVICIOS ---------------------------------------------------------
def get_all_services(only_active=False) -> pd.DataFrame:
    df = _load_df("servicios")
    if only_active:
        df = df[df["activo"] == True]
    return df

def get_service_by_id(sid: int) -> dict | None:
    df = _load_df("servicios")
    row = df[df["id"] == sid]
    return row.iloc[0].to_dict() if not row.empty else None

def create_service(nombre, precio, duracion_min, categoria) -> int:
    nid = _next_id("servicios")
    _insert_row("servicios", {
        "id": nid, "nombre": nombre, "precio": precio,
        "duracion_min": duracion_min, "categoria": categoria,
        "activo": True,
        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    return nid

def update_service(sid: int, **kwargs):
    df = _load_df("servicios")
    idx = df.index[df["id"] == sid]
    if idx.empty:
        return False
    for k, v in kwargs.items():
        if k in df.columns:
            df.at[idx[0], k] = v
    _save_df("servicios", df)
    return True

def delete_service(sid: int):
    df = _load_df("servicios")
    df = df[df["id"] != sid]
    _save_df("servicios", df)


# ---------- CITAS -------------------------------------------------------------
def get_all_appointments() -> pd.DataFrame:
    return _load_df("citas")

def get_appointments_by_client(client_id: int) -> pd.DataFrame:
    df = _load_df("citas")
    return df[df["cliente_id"] == client_id]

def get_appointments_by_barber_date(barber_id: int, date_str: str) -> pd.DataFrame:
    df = _load_df("citas")
    mask = (df["barbero_id"] == barber_id) & (df["fecha"] == date_str) & (df["estado"] != "Cancelada")
    return df[mask]

def get_available_slots(barber_id: int, date_str: str, duration_min: int) -> list[str]:
    """Calcula los slots disponibles para un barbero en una fecha dada."""
    barber = get_barber_by_id(barber_id)
    if not barber:
        return []

    from datetime import datetime, timedelta

    start = datetime.strptime(f"{date_str} {barber['hora_inicio']}", "%Y-%m-%d %H:%M")
    end   = datetime.strptime(f"{date_str} {barber['hora_fin']}",   "%Y-%m-%d %H:%M")

    # Construir lista de slots cada 15 minutos
    slots = []
    current = start
    while current + timedelta(minutes=duration_min) <= end:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=15)

    # Filtrar los ocupados
    booked = get_appointments_by_barber_date(barber_id, date_str)
    for _, row in booked.iterrows():
        try:
            b_start = datetime.strptime(f"{date_str} {row['hora_inicio']}", "%Y-%m-%d %H:%M")
            b_end   = datetime.strptime(f"{date_str} {row['hora_fin']}",   "%Y-%m-%d %H:%M")
            slots = [
                s for s in slots
                if not (
                    datetime.strptime(f"{date_str} {s}", "%Y-%m-%d %H:%M") < b_end
                    and datetime.strptime(f"{date_str} {s}", "%Y-%m-%d %H:%M") + timedelta(minutes=duration_min) > b_start
                )
            ]
        except Exception:
            pass

    return slots

def create_appointment(cliente_id, cliente_nombre, barbero_id, barbero_nombre,
                        servicio_id, servicio_nombre, precio, fecha,
                        hora_inicio, hora_fin, notas="") -> int:
    nid = _next_id("citas")
    _insert_row("citas", {
        "id": nid,
        "cliente_id": cliente_id, "cliente_nombre": cliente_nombre,
        "barbero_id": barbero_id, "barbero_nombre": barbero_nombre,
        "servicio_id": servicio_id, "servicio_nombre": servicio_nombre,
        "precio": precio, "fecha": fecha,
        "hora_inicio": hora_inicio, "hora_fin": hora_fin,
        "estado": "Pendiente", "notas": notas,
        "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    logger.info("Cita creada id=%d para cliente %s el %s %s", nid, cliente_nombre, fecha, hora_inicio)
    return nid

def update_appointment(cid: int, **kwargs):
    df = _load_df("citas")
    idx = df.index[df["id"] == cid]
    if idx.empty:
        return False
    for k, v in kwargs.items():
        if k in df.columns:
            df.at[idx[0], k] = v
    _save_df("citas", df)
    logger.info("Cita id=%d actualizada: %s", cid, kwargs)
    return True

def cancel_appointment(cid: int):
    return update_appointment(cid, estado="Cancelada")
