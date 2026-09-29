# FiscalAI — Landing page y CRM para automatización contable

Sitio web y backend de **FiscalAI**, una propuesta de automatización contable para PYMES colombianas: de la factura electrónica DIAN al análisis fiscal. El proyecto incluye la landing pública, las páginas comerciales, un panel de administración tipo CRM y una API para capturar y gestionar leads.

Desplegado en Fly.io con despliegue continuo desde GitHub Actions.

## Qué incluye

**Sitio público** (`static/`, HTML/CSS/JS sin paso de build)

| Página | Contenido |
| --- | --- |
| `index.html` | Landing principal con planes de precios y formulario de acceso a la demo |
| `pages/demo.html` | Demostración visual del flujo de procesamiento fiscal (XML DIAN → análisis) |
| `pages/empresas.html` | Página para empresas con formulario hero y formulario de contacto |
| `pages/problematica.html` | Planteamiento del problema que resuelve el producto |
| `pages/pitch.html` | Pitch deck |
| `pages/ga4-tracking.html` | Arquitectura de analítica GA4 y eventos |
| `pages/admin.html` | Panel de administración (CRM) |

**API** (`app/`, FastAPI)

- Captura de leads desde cuatro formularios: demo, hero de empresas, contacto y planes de precios.
- Panel administrativo protegido con clave: pipeline de leads por etapa, analítica, clientes, suscripciones, requerimientos por cliente y envío de correos con registro de historial.
- Registro de la IP del cliente respetando `X-Forwarded-For` (detrás del proxy de Fly.io).
- Duplicados silenciosos en los leads de demo y hero, para no bloquear al usuario.
- Documentación interactiva automática en `/api/docs` (Swagger) y `/api/redoc`.

## Tecnologías

- **Backend:** Python 3.11, FastAPI, SQLAlchemy, Pydantic, Uvicorn
- **Base de datos:** SQLite (configurable con `DATABASE_URL`)
- **Frontend:** HTML, CSS y JavaScript vanilla
- **Correo transaccional:** Resend
- **Despliegue:** Docker, Fly.io (con volumen persistente) y GitHub Actions

## Cómo ejecutarlo

```bash
git clone https://github.com/Alejob12/FiscalIA-langing-page.git
cd FiscalIA-langing-page

python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

Abre `http://localhost:8000`. La base de datos `fiscalai.db` se crea sola en el primer arranque.

Con Docker:

```bash
docker build -t fiscalai .
docker run -p 8000:8000 -e ADMIN_API_KEY=cambia-esto fiscalai
```

## Variables de entorno

| Variable | Por defecto | Uso |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./fiscalai.db` | Cadena de conexión de SQLAlchemy |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | Orígenes permitidos por CORS, separados por comas |
| `ADMIN_API_KEY` | — | Clave requerida (cabecera `X-Admin-Key`) para los endpoints de consulta y administración; si no está definida, responden 503 |
| `RESEND_API_KEY` | — | Clave de Resend para enviar correos desde el panel |
| `RESEND_FROM_EMAIL` | `FiscalAI <onboarding@resend.dev>` | Remitente de los correos |

## Endpoints principales

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/api/health` | Estado del servicio |
| `POST` | `/api/leads/demo` · `/api/leads/hero` · `/api/leads/pricing` | Registro de leads |
| `POST` | `/api/contacts` | Formulario de contacto |
| `GET` | `/api/admin/leads`, `/api/admin/analytics` | Pipeline y analítica (requiere `X-Admin-Key`) |
| `GET/POST/PUT` | `/api/admin/clients`, `/subscriptions`, `/requirements` | Gestión de clientes, suscripciones y requerimientos |
| `POST` | `/api/admin/send-email` | Envío de correo y registro en historial |

La lista completa y los esquemas están en `/api/docs`.

## Estructura

```
app/
  main.py        Rutas de la API y servido de archivos estáticos
  models.py      Modelos SQLAlchemy (leads, clientes, suscripciones, correos)
  schemas.py     Esquemas Pydantic de entrada y salida
  database.py    Motor, sesión y dependencia get_db
static/
  index.html     Landing
  css/ js/       Estilos y lógica del sitio
  pages/         Páginas comerciales, demo y panel de administración
Dockerfile       Imagen de producción
fly.toml         Configuración de Fly.io (región dfw, volumen /data)
.github/workflows/deploy.yml   Despliegue a Fly.io en cada push a main
```

## Notas

- La página de demo muestra el flujo de procesamiento de forma visual; no procesa facturas reales.
- Proyecto de emprendimiento en etapa temprana.

## Autor

**Alejandro Bernal** — Ingeniería de Sistemas e Industrial, Universidad de los Andes.
