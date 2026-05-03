from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
import re


# ─── Demo Lead (index.html — demo gate) ───────────────────────────────────────

class DemoLeadCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    company: str
    role: Optional[str] = None
    volume: Optional[str] = None
    source: Optional[str] = "demo_gate"

    @field_validator("name", "company", "phone")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Este campo no puede estar vacío")
        return v.strip()


class DemoLeadOut(DemoLeadCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Hero Lead (empresas.html — sección hero) ─────────────────────────────────

class HeroLeadCreate(BaseModel):
    nombre: str
    email: EmailStr
    empresa: str
    volumen: Optional[str] = None
    source: Optional[str] = "hero_form"

    @field_validator("nombre", "empresa")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Este campo no puede estar vacío")
        return v.strip()


class HeroLeadOut(HeroLeadCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Contact Form (empresas.html — formulario de contacto) ────────────────────

class ContactFormCreate(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    empresa: str
    nit: Optional[str] = None
    volumen: Optional[str] = None
    software: Optional[str] = None
    mensaje: Optional[str] = None
    source: Optional[str] = "contact_form"

    @field_validator("nombre", "apellido", "empresa")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Este campo no puede estar vacío")
        return v.strip()


class ContactFormOut(ContactFormCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Pricing Lead (index.html — modal de planes) ──────────────────────────────

class PricingLeadCreate(BaseModel):
    name: str
    email: EmailStr
    plan: str
    message: str
    source: Optional[str] = "pricing_modal"

    @field_validator("name", "plan", "message")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Este campo no puede estar vacío")
        return v.strip()


class PricingLeadOut(PricingLeadCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── CRM / Pipeline ───────────────────────────────────────────────────────────

class LeadStageUpdate(BaseModel):
    lead_type: str   # demo | hero | pricing | contact
    lead_id: int
    stage: str       # nuevo | contactado | negociacion | cliente | perdido
    notes: Optional[str] = None


# ─── Clients ──────────────────────────────────────────────────────────────────

class ClientCreate(BaseModel):
    nombre: str
    email: EmailStr
    empresa: Optional[str] = None
    telefono: Optional[str] = None
    plan: Optional[str] = None
    status: Optional[str] = "activo"
    notes: Optional[str] = None

    @field_validator("nombre")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()


class ClientUpdate(BaseModel):
    nombre: Optional[str] = None
    empresa: Optional[str] = None
    telefono: Optional[str] = None
    plan: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ClientOut(ClientCreate):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Subscriptions ────────────────────────────────────────────────────────────

class SubscriptionCreate(BaseModel):
    client_id: int
    plan: str
    amount_cop: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = "activo"
    notes: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    plan: Optional[str] = None
    amount_cop: Optional[int] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class SubscriptionOut(SubscriptionCreate):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Requirements ─────────────────────────────────────────────────────────────

class RequirementCreate(BaseModel):
    client_id: int
    titulo: str
    descripcion: Optional[str] = None
    prioridad: Optional[str] = "media"
    status: Optional[str] = "abierto"


class RequirementUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    prioridad: Optional[str] = None
    status: Optional[str] = None


class RequirementOut(RequirementCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ─── Email ────────────────────────────────────────────────────────────────────

class SendEmailRequest(BaseModel):
    to_email: EmailStr
    to_name: Optional[str] = None
    subject: str
    body_html: str
    lead_type: Optional[str] = None
    lead_id: Optional[int] = None
    client_id: Optional[int] = None


class EmailLogOut(BaseModel):
    id: int
    to_email: str
    to_name: Optional[str]
    subject: str
    status: str
    error_msg: Optional[str]
    lead_type: Optional[str]
    lead_id: Optional[int]
    client_id: Optional[int]
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Generic response ─────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    ok: bool
    message: str
    id: Optional[int] = None
