from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from .database import Base


class DemoLead(Base):
    """
    Leads capturados en el formulario gate de la demo (index.html).
    Campos: nombre, email, teléfono, empresa, rol, volumen de facturas.
    """
    __tablename__ = "demo_leads"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(120), nullable=False)
    email       = Column(String(180), nullable=False, index=True)
    phone       = Column(String(30), nullable=False)
    company     = Column(String(150), nullable=False)
    role        = Column(String(60), nullable=True)   # contador, empresario, gerente…
    volume      = Column(String(30), nullable=True)   # 1-15, 16-50, 51-200…
    source      = Column(String(50), default="demo_gate")
    ip_address  = Column(String(50), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class HeroLead(Base):
    """
    Leads del formulario Hero de la página Empresas (empresas.html, sección superior).
    Campos: nombre, email, empresa, volumen de facturas.
    """
    __tablename__ = "hero_leads"

    id         = Column(Integer, primary_key=True, index=True)
    nombre     = Column(String(120), nullable=False)
    email      = Column(String(180), nullable=False, index=True)
    empresa    = Column(String(150), nullable=False)
    volumen    = Column(String(50), nullable=True)   # 100-500, 500-1000…
    source     = Column(String(50), default="hero_form")
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ContactForm(Base):
    """
    Formulario de contacto completo en la página Empresas (empresas.html).
    Campos: nombre, apellido, email, empresa, NIT, volumen, software actual, mensaje.
    """
    __tablename__ = "contact_forms"

    id         = Column(Integer, primary_key=True, index=True)
    nombre     = Column(String(120), nullable=False)
    apellido   = Column(String(120), nullable=False)
    email      = Column(String(180), nullable=False, index=True)
    empresa    = Column(String(150), nullable=False)
    nit        = Column(String(30), nullable=True)
    volumen    = Column(String(50), nullable=True)   # 100-500, 500-1000…
    software   = Column(String(80), nullable=True)   # Siigo, World Office, SAP…
    mensaje    = Column(Text, nullable=True)
    source     = Column(String(50), default="contact_form")
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PricingLead(Base):
    """
    Mensajes capturados desde el modal de planes de precios (index.html).
    Campos: nombre, email, plan seleccionado, mensaje libre.
    """
    __tablename__ = "pricing_leads"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(120), nullable=False)
    email      = Column(String(180), nullable=False, index=True)
    plan       = Column(String(60), nullable=False)   # Freemium, PYME Pro, Enterprise
    message    = Column(Text, nullable=False)
    source     = Column(String(50), default="pricing_modal")
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ─── CRM / Admin models ───────────────────────────────────────────────────────

class LeadPipeline(Base):
    """Etapa del pipeline para cada lead (de cualquier fuente)."""
    __tablename__ = "lead_pipeline"

    id         = Column(Integer, primary_key=True, index=True)
    lead_type  = Column(String(20), nullable=False)   # demo, hero, pricing, contact
    lead_id    = Column(Integer, nullable=False)
    stage      = Column(String(30), default="nuevo", nullable=False)
    # nuevo | contactado | negociacion | cliente | perdido
    notes      = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("lead_type", "lead_id", name="uq_lead_pipeline"),
    )


class Client(Base):
    """Clientes activos (convertidos desde leads)."""
    __tablename__ = "clients"

    id         = Column(Integer, primary_key=True, index=True)
    nombre     = Column(String(120), nullable=False)
    email      = Column(String(180), nullable=False, index=True)
    empresa    = Column(String(150), nullable=True)
    telefono   = Column(String(30), nullable=True)
    plan       = Column(String(60), nullable=True)    # Freemium, PYME Pro, Enterprise
    status     = Column(String(20), default="activo") # activo, pausado, cancelado
    notes      = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Subscription(Base):
    """Historial de suscripciones por cliente."""
    __tablename__ = "subscriptions"

    id          = Column(Integer, primary_key=True, index=True)
    client_id   = Column(Integer, nullable=False, index=True)
    plan        = Column(String(60), nullable=False)
    amount_cop  = Column(Integer, nullable=True)       # monto mensual en COP
    start_date  = Column(DateTime(timezone=True), server_default=func.now())
    end_date    = Column(DateTime(timezone=True), nullable=True)
    status      = Column(String(20), default="activo") # activo, renovado, cancelado
    notes       = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class ClientRequirement(Base):
    """Requerimientos o solicitudes de un cliente activo."""
    __tablename__ = "client_requirements"

    id          = Column(Integer, primary_key=True, index=True)
    client_id   = Column(Integer, nullable=False, index=True)
    titulo      = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    prioridad   = Column(String(20), default="media")  # alta, media, baja
    status      = Column(String(30), default="abierto")
    # abierto | en_progreso | resuelto | cerrado
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), server_default=func.now())


class EmailLog(Base):
    """Registro de correos enviados desde el panel de admin."""
    __tablename__ = "email_logs"

    id          = Column(Integer, primary_key=True, index=True)
    to_email    = Column(String(180), nullable=False)
    to_name     = Column(String(120), nullable=True)
    subject     = Column(String(300), nullable=False)
    body_html   = Column(Text, nullable=False)
    status      = Column(String(20), default="sent")   # sent, failed
    error_msg   = Column(Text, nullable=True)
    lead_type   = Column(String(20), nullable=True)
    lead_id     = Column(Integer, nullable=True)
    client_id   = Column(Integer, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
