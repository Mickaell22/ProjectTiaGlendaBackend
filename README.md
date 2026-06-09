# Centro Tía Glenda — Backend

API REST para sistema de gestión de centro terapéutico y pedagógico. Módulos de pacientes, sesiones de terapia, sesiones pedagógicas, personal, facturación, chat y notificaciones. Desplegado en Railway.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)

---

## Módulos

| Módulo | Descripción |
|--------|-------------|
| **Auth** | JWT con roles (admin, terapeuta, pedagogo) |
| **Personas** | CRUD de pacientes, personal y tutores |
| **Sesiones de terapia** | Programación automática, asistencias, cronogramas |
| **Sesiones pedagógicas** | Clases con cronograma y asistencias |
| **Especialidades** | Catálogo de especialidades del centro |
| **Facturación** | Generación de facturas por sesión |
| **Chat** | Mensajería interna entre usuarios |
| **Notificaciones** | Sistema de alertas en tiempo real |
| **Reportes** | Exportación de datos y estadísticas |
| **Dashboard** | KPIs por rol (admin, terapeuta, pedagogo) |
| **Multi-centro** | Soporte para múltiples sucursales con RBAC |

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Framework | Flask (Python) |
| Base de datos | PostgreSQL |
| Auth | JWT (`flask-jwt-extended`) |
| Documentación | Swagger UI (`/static/swagger.json`) |
| Deploy | Railway (Nixpacks + Gunicorn) |
| Tests | pytest — 20+ archivos de test |

---

## Variables de entorno

```env
DATABASE_URL=postgresql://user:password@host:5432/db
JWT_SECRET=your-jwt-secret
AMBIENTE=PRODUCTION
```

---

## Correr localmente

```bash
git clone https://github.com/Mickaell22/ProjectTiaGlendaBackend.git
cd ProjectTiaGlendaBackend
pip install -r requirements.txt
```

Configura `src/utils/database/config_db.txt` con tus credenciales de PostgreSQL, luego:

```bash
python app.py
```

API en `http://localhost:5000` · Swagger en `http://localhost:5000/static/swagger.json`

---

## Frontend

Consumido por [ProjectTiaGlendaFrontend](https://github.com/Mickaell22/ProjectTiaGlendaFrontend) — React + Vite + Material UI.
