import os
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import engine, get_db, Base
from . import models, schemas

# ─── Crear tablas al arrancar ─────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FiscalAI — API de Leads",
    description="Backend para recepción y almacenamiento de leads de los formularios de FiscalAI.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Agrega aquí tu dominio real en producción, ej: "https://fiscalai.com"
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_client_ip(request: Request) -> str:
    """Obtiene la IP real del cliente, considerando proxies (Fly.io / Cloudflare)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ─── Health check ─────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["Sistema"])
def health_check():
    return {"status": "ok", "service": "FiscalAI API"}


# ─── Demo Lead (index.html — gate de demo) ────────────────────────────────────

@app.post(
    "/api/leads/demo",
    response_model=schemas.MessageResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Leads"],
    summary="Registra un lead desde el formulario de acceso a la demo",
)
def create_demo_lead(
    lead: schemas.DemoLeadCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    # Evitar duplicados por email
    existing = db.query(models.DemoLead).filter(
        models.DemoLead.email == lead.email
    ).first()
    if existing:
        # No es un error — simplemente devolvemos OK para no bloquear el acceso
        return schemas.MessageResponse(
            ok=True,
            message="Lead ya registrado anteriormente.",
            id=existing.id,
        )

    db_lead = models.DemoLead(
        **lead.model_dump(),
        ip_address=get_client_ip(request),
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return schemas.MessageResponse(
        ok=True,
        message="¡Gracias! Ya puedes acceder a la demo.",
        id=db_lead.id,
    )


@app.get(
    "/api/leads/demo",
    response_model=List[schemas.DemoLeadOut],
    tags=["Leads"],
    summary="Lista todos los demo leads (protegido con API key)",
)
def list_demo_leads(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    _require_admin(request)
    return db.query(models.DemoLead).order_by(
        models.DemoLead.created_at.desc()
    ).offset(skip).limit(limit).all()


# ─── Hero Lead (empresas.html — sección hero) ─────────────────────────────────

@app.post(
    "/api/leads/hero",
    response_model=schemas.MessageResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Leads"],
    summary="Registra un lead desde el formulario hero de Empresas",
)
def create_hero_lead(
    lead: schemas.HeroLeadCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    existing = db.query(models.HeroLead).filter(
        models.HeroLead.email == lead.email
    ).first()
    if existing:
        return schemas.MessageResponse(
            ok=True,
            message="Lead ya registrado.",
            id=existing.id,
        )

    db_lead = models.HeroLead(
        **lead.model_dump(),
        ip_address=get_client_ip(request),
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return schemas.MessageResponse(
        ok=True,
        message="¡Gracias! Pronto te contactaremos.",
        id=db_lead.id,
    )


@app.get(
    "/api/leads/hero",
    response_model=List[schemas.HeroLeadOut],
    tags=["Leads"],
    summary="Lista todos los hero leads (protegido con API key)",
)
def list_hero_leads(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    _require_admin(request)
    return db.query(models.HeroLead).order_by(
        models.HeroLead.created_at.desc()
    ).offset(skip).limit(limit).all()


# ─── Contact Form (empresas.html — formulario completo) ───────────────────────

@app.post(
    "/api/contacts",
    response_model=schemas.MessageResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Contactos"],
    summary="Registra una solicitud del formulario de contacto completo",
)
def create_contact(
    contact: schemas.ContactFormCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    db_contact = models.ContactForm(
        **contact.model_dump(),
        ip_address=get_client_ip(request),
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return schemas.MessageResponse(
        ok=True,
        message="¡Gracias! Hemos recibido tu mensaje y te contactaremos pronto.",
        id=db_contact.id,
    )


@app.get(
    "/api/contacts",
    response_model=List[schemas.ContactFormOut],
    tags=["Contactos"],
    summary="Lista todos los formularios de contacto (protegido con API key)",
)
def list_contacts(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    _require_admin(request)
    return db.query(models.ContactForm).order_by(
        models.ContactForm.created_at.desc()
    ).offset(skip).limit(limit).all()


# ─── Admin guard ──────────────────────────────────────────────────────────────

def _require_admin(request: Request):
    """
    Protección mínima para los endpoints GET.
    Pasa la API key como header: X-Admin-Key: <valor de ADMIN_API_KEY>
    """
    api_key = os.getenv("ADMIN_API_KEY", "")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADMIN_API_KEY no configurada en el servidor.",
        )
    provided = request.headers.get("X-Admin-Key", "")
    if provided != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida.",
        )

# ─── Pricing Lead (index.html — modal de planes de precios) ───────────────────

@app.post(
    "/api/leads/pricing",
    response_model=schemas.MessageResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Leads"],
    summary="Registra un mensaje desde el modal de planes de precios",
)
def create_pricing_lead(
    lead: schemas.PricingLeadCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    db_lead = models.PricingLead(
        **lead.model_dump(),
        ip_address=get_client_ip(request),
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return schemas.MessageResponse(
        ok=True,
        message="¡Gracias! Un asesor te contactará pronto.",
        id=db_lead.id,
    )


@app.get(
    "/api/leads/pricing",
    response_model=List[schemas.PricingLeadOut],
    tags=["Leads"],
    summary="Lista todos los pricing leads (protegido con API key)",
)
def list_pricing_leads(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    _require_admin(request)
    return db.query(models.PricingLead).order_by(
        models.PricingLead.created_at.desc()
    ).offset(skip).limit(limit).all()


# ─── Servir archivos estáticos (frontend) ─────────────────────────────────────
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
app.mount("/pages", StaticFiles(directory="static/pages"), name="pages")

@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse("static/index.html")

# Catch-all para rutas del frontend
@app.get("/{full_path:path}", include_in_schema=False)
def serve_static(full_path: str):
    import os
    file_path = f"static/{full_path}"
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse("static/index.html")






# ─── Error handler global ─────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"ok": False, "message": "Error interno del servidor."},
    )
