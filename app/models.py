from sqlalchemy import Column, Integer, String, Text, DateTime
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
