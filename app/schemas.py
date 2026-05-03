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


# ─── Generic response ─────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    ok: bool
    message: str
    id: Optional[int] = None
