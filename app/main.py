import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Any, Dict
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
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
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


# ─── Email helper (Resend) ────────────────────────────────────────────────────

def _send_via_resend(to_email: str, to_name: str | None, subject: str, body_html: str) -> tuple[bool, str]:
    api_key = os.getenv("RESEND_API_KEY", "")
    if not api_key:
        return False, "RESEND_API_KEY no configurada en el servidor."
    from_addr = os.getenv("RESEND_FROM_EMAIL", "FiscalAI <onboarding@resend.dev>")
    to_addr = f"{to_name} <{to_email}>" if to_name else to_email
    payload = json.dumps({"from": from_addr, "to": [to_addr], "subject": subject, "html": body_html}).encode()
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "fiscalai-backend/1.0",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True, json.loads(resp.read()).get("id", "ok")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:400]
        return False, f"HTTP {e.code}: {body}"
    except Exception as exc:
        return False, str(exc)[:400]


# ─── Admin: leads unificados + pipeline ───────────────────────────────────────

@app.get("/api/admin/leads", tags=["Admin"])
def list_all_leads(request: Request, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    _require_admin(request)

    def get_stage(lead_type: str, lead_id: int):
        row = db.query(models.LeadPipeline).filter_by(lead_type=lead_type, lead_id=lead_id).first()
        return {"stage": row.stage if row else "nuevo", "notes": row.notes if row else ""}

    result: List[Dict[str, Any]] = []

    for lead in db.query(models.DemoLead).order_by(models.DemoLead.created_at.desc()).all():
        s = get_stage("demo", lead.id)
        result.append({"type": "demo", "id": lead.id, "nombre": lead.name, "email": lead.email,
                        "empresa": lead.company, "telefono": lead.phone,
                        "extra": {"rol": lead.role, "volumen": lead.volume},
                        "stage": s["stage"], "notes": s["notes"],
                        "created_at": lead.created_at.isoformat() if lead.created_at else None})

    for lead in db.query(models.HeroLead).order_by(models.HeroLead.created_at.desc()).all():
        s = get_stage("hero", lead.id)
        result.append({"type": "hero", "id": lead.id, "nombre": lead.nombre, "email": lead.email,
                        "empresa": lead.empresa, "telefono": None,
                        "extra": {"volumen": lead.volumen},
                        "stage": s["stage"], "notes": s["notes"],
                        "created_at": lead.created_at.isoformat() if lead.created_at else None})

    for lead in db.query(models.PricingLead).order_by(models.PricingLead.created_at.desc()).all():
        s = get_stage("pricing", lead.id)
        result.append({"type": "pricing", "id": lead.id, "nombre": lead.name, "email": lead.email,
                        "empresa": None, "telefono": None,
                        "extra": {"plan": lead.plan, "mensaje": lead.message},
                        "stage": s["stage"], "notes": s["notes"],
                        "created_at": lead.created_at.isoformat() if lead.created_at else None})

    for lead in db.query(models.ContactForm).order_by(models.ContactForm.created_at.desc()).all():
        s = get_stage("contact", lead.id)
        result.append({"type": "contact", "id": lead.id,
                        "nombre": f"{lead.nombre} {lead.apellido}", "email": lead.email,
                        "empresa": lead.empresa, "telefono": None,
                        "extra": {"nit": lead.nit, "volumen": lead.volumen,
                                  "software": lead.software, "mensaje": lead.mensaje},
                        "stage": s["stage"], "notes": s["notes"],
                        "created_at": lead.created_at.isoformat() if lead.created_at else None})

    result.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return result


@app.put("/api/admin/leads/stage", tags=["Admin"])
def update_lead_stage(payload: schemas.LeadStageUpdate, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    row = db.query(models.LeadPipeline).filter_by(lead_type=payload.lead_type, lead_id=payload.lead_id).first()
    now = datetime.now(timezone.utc)
    if row:
        row.stage = payload.stage
        if payload.notes is not None:
            row.notes = payload.notes
        row.updated_at = now
    else:
        row = models.LeadPipeline(lead_type=payload.lead_type, lead_id=payload.lead_id,
                                   stage=payload.stage, notes=payload.notes or "", updated_at=now)
        db.add(row)
    db.commit()
    return {"ok": True}


# ─── Admin: analytics ─────────────────────────────────────────────────────────

@app.get("/api/admin/analytics", tags=["Admin"])
def get_analytics(request: Request, db: Session = Depends(get_db)):
    _require_admin(request)

    demo_cnt    = db.query(models.DemoLead).count()
    hero_cnt    = db.query(models.HeroLead).count()
    pricing_cnt = db.query(models.PricingLead).count()
    contact_cnt = db.query(models.ContactForm).count()
    total_leads = demo_cnt + hero_cnt + pricing_cnt + contact_cnt

    tracked = db.query(models.LeadPipeline).count()
    stage_counts: Dict[str, int] = {}
    for st in ["nuevo", "contactado", "negociacion", "cliente", "perdido"]:
        stage_counts[st] = db.query(models.LeadPipeline).filter_by(stage=st).count()
    stage_counts["nuevo"] += max(0, total_leads - tracked)

    clients_active = db.query(models.Client).filter_by(status="activo").count()
    clients_total  = db.query(models.Client).count()

    active_subs = db.query(models.Subscription).filter_by(status="activo").all()
    mrr = sum(s.amount_cop or 0 for s in active_subs)

    total_subs  = db.query(models.Subscription).count()
    renewed     = db.query(models.Subscription).filter_by(status="renovado").count()
    renewal_rate = round(renewed / total_subs, 2) if total_subs > 0 else 0

    conversion = round(clients_active / total_leads * 100, 1) if total_leads > 0 else 0

    return {
        "leads": {"total": total_leads, "by_source": {"demo": demo_cnt, "hero": hero_cnt,
                   "pricing": pricing_cnt, "contact": contact_cnt}, "by_stage": stage_counts},
        "clients": {"total": clients_total, "active": clients_active},
        "revenue": {"mrr": mrr, "arr": mrr * 12},
        "subscriptions": {"total": total_subs, "active": len(active_subs), "renewal_rate": renewal_rate},
        "conversion_rate": conversion,
    }


# ─── Admin: clientes ──────────────────────────────────────────────────────────

@app.get("/api/admin/clients", response_model=List[schemas.ClientOut], tags=["Admin"])
def list_clients(request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    return db.query(models.Client).order_by(models.Client.created_at.desc()).all()


@app.post("/api/admin/clients", response_model=schemas.ClientOut, status_code=201, tags=["Admin"])
def create_client(payload: schemas.ClientCreate, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    c = models.Client(**payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@app.put("/api/admin/clients/{client_id}", response_model=schemas.ClientOut, tags=["Admin"])
def update_client(client_id: int, payload: schemas.ClientUpdate, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    c = db.query(models.Client).filter_by(id=client_id).first()
    if not c:
        raise HTTPException(404, "Cliente no encontrado")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


# ─── Admin: suscripciones ─────────────────────────────────────────────────────

@app.get("/api/admin/subscriptions", response_model=List[schemas.SubscriptionOut], tags=["Admin"])
def list_subscriptions(request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    return db.query(models.Subscription).order_by(models.Subscription.created_at.desc()).all()


@app.post("/api/admin/subscriptions", response_model=schemas.SubscriptionOut, status_code=201, tags=["Admin"])
def create_subscription(payload: schemas.SubscriptionCreate, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    data = payload.model_dump()
    if not data.get("start_date"):
        data["start_date"] = datetime.now(timezone.utc)
    s = models.Subscription(**data)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@app.put("/api/admin/subscriptions/{sub_id}", response_model=schemas.SubscriptionOut, tags=["Admin"])
def update_subscription(sub_id: int, payload: schemas.SubscriptionUpdate, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    s = db.query(models.Subscription).filter_by(id=sub_id).first()
    if not s:
        raise HTTPException(404, "Suscripción no encontrada")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


# ─── Admin: requerimientos ────────────────────────────────────────────────────

@app.get("/api/admin/requirements", response_model=List[schemas.RequirementOut], tags=["Admin"])
def list_requirements(request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    return db.query(models.ClientRequirement).order_by(models.ClientRequirement.created_at.desc()).all()


@app.post("/api/admin/requirements", response_model=schemas.RequirementOut, status_code=201, tags=["Admin"])
def create_requirement(payload: schemas.RequirementCreate, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    r = models.ClientRequirement(**payload.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@app.put("/api/admin/requirements/{req_id}", response_model=schemas.RequirementOut, tags=["Admin"])
def update_requirement(req_id: int, payload: schemas.RequirementUpdate, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    r = db.query(models.ClientRequirement).filter_by(id=req_id).first()
    if not r:
        raise HTTPException(404, "Requerimiento no encontrado")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(r, k, v)
    r.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(r)
    return r


# ─── Admin: correos ───────────────────────────────────────────────────────────

@app.post("/api/admin/send-email", tags=["Admin"])
def send_email(payload: schemas.SendEmailRequest, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    ok, msg = _send_via_resend(str(payload.to_email), payload.to_name, payload.subject, payload.body_html)
    log = models.EmailLog(
        to_email=str(payload.to_email), to_name=payload.to_name,
        subject=payload.subject, body_html=payload.body_html,
        status="sent" if ok else "failed", error_msg=None if ok else msg,
        lead_type=payload.lead_type, lead_id=payload.lead_id, client_id=payload.client_id,
    )
    db.add(log)
    db.commit()
    if not ok:
        raise HTTPException(502, detail=msg)
    return {"ok": True, "resend_id": msg}


@app.get("/api/admin/emails", response_model=List[schemas.EmailLogOut], tags=["Admin"])
def list_emails(request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    return db.query(models.EmailLog).order_by(models.EmailLog.created_at.desc()).limit(200).all()


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
