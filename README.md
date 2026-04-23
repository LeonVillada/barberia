# ✂ Barbería Pro — Sistema de Gestión de Agenda

Aplicación de escritorio construida con **Python + Tkinter** para gestionar la agenda de una barbería. Incluye panel de administrador, portal de cliente, calendario dinámico de disponibilidad y persistencia en Excel.

---

## 📁 Estructura del Proyecto

```
barberia/
├── main.py                  # Punto de entrada y controlador de rutas
├── requirements.txt
├── database.xlsx            # Se crea automáticamente al primer inicio
├── core/
│   ├── __init__.py
│   ├── database.py          # Capa de datos (CRUD sobre Excel)
│   └── styles.py            # Paleta de colores, fuentes, constantes
└── ui/
    ├── __init__.py
    ├── widgets.py            # Componentes reutilizables (botones, cards, etc.)
    ├── auth_view.py          # Login y Registro
    ├── admin_view.py         # Panel administrador (Dashboard, Barberos, Servicios, Citas)
    └── client_view.py        # Panel cliente (Reserva, Mis Citas, Perfil)
```

---

## 🚀 Instalación y Ejecución

### 1. Clonar o descomprimir el proyecto
```bash
cd barberia
```

### 2. Crear entorno virtual (recomendado)
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```bash
python main.py
```

---

## 🔐 Credenciales por defecto

| Rol           | Email                    | Contraseña |
|---------------|--------------------------|------------|
| Administrador | admin@barberia.com       | admin123   |
| Cliente       | (crear desde registro)   | —          |

---

## 👤 Funcionalidades por Rol

### Administrador
- **Dashboard**: estadísticas de citas, últimas reservas
- **Barberos**: CRUD completo con horarios y estado activo/inactivo
- **Servicios**: CRUD con precio, duración y categoría
- **Citas**: filtros por fecha/barbero/estado, cambio de estado
- **Clientes**: listado de usuarios registrados

### Cliente
- Registro e inicio de sesión
- **Reservar Cita** (wizard de 4 pasos):
  1. Elegir barbero
  2. Elegir servicio
  3. Seleccionar fecha en calendario visual + horario disponible
  4. Confirmar resumen
- **Mis Citas**: historial, filtro por estado, cancelación
- **Perfil**: datos personales

---

## 📊 Base de Datos (Excel)

El archivo `database.xlsx` contiene 4 hojas:

| Hoja       | Descripción                        |
|------------|------------------------------------|
| usuarios   | Clientes y administradores         |
| barberos   | Staff con horarios                 |
| servicios  | Catálogo de servicios              |
| citas      | Todas las reservas con estado      |

---

## 📦 Generar Ejecutable (.exe)

```bash
pyinstaller --onefile --windowed --add-data "database.xlsx;." main.py
```

### Opciones adicionales recomendadas:
```bash
pyinstaller ^
  --onefile ^
  --windowed ^
  --add-data "database.xlsx;." ^
  --name "BarberiaPro" ^
  --icon "assets/icon.ico" ^
  main.py
```

> **Nota**: Si `database.xlsx` no existe aún, ejecuta la app al menos una vez para que se genere antes de empaquetar. También puedes crear un archivo vacío con la estructura correcta para incluirlo en el .exe.

El ejecutable queda en `dist/BarberiaPro.exe`.

---

## 🔧 Solución de Problemas

| Problema                         | Solución                                              |
|----------------------------------|-------------------------------------------------------|
| `ModuleNotFoundError: pandas`    | Ejecutar `pip install -r requirements.txt`            |
| El .exe no encuentra database    | Usar `--add-data "database.xlsx;."` en PyInstaller    |
| Fuente Segoe UI no disponible    | Solo afecta Linux/macOS; cambiar a `Arial` en styles.py |
| Pantalla muy pequeña             | Escalar ventana desde la esquina o ajustar `WINDOW` en styles.py |

---

## 🎨 Personalización

- **Colores**: editar `core/styles.py` → diccionario `COLORS`
- **Nombre de la barbería**: buscar `"BARBERÍA PRO"` en `auth_view.py` y `admin_view.py`
- **Barberos/servicios iniciales**: función `init_database()` en `core/database.py`
