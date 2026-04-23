from __future__ import annotations
import uuid
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# ── Patients ─────────────────────────────────────────────────────────────────

class PatientCreate(BaseModel):
    full_name: str
    first_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class PatientOut(BaseModel):
    id: uuid.UUID
    full_name: str
    first_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Appointments ─────────────────────────────────────────────────────────────

class AppointmentCreate(BaseModel):
    patient_id: uuid.UUID
    appointment_type: str
    appointment_date: Optional[datetime] = None
    provider_name: Optional[str] = None
    clinic_location: Optional[str] = None
    appointment_description: Optional[str] = None


class AppointmentOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    appointment_type: str
    appointment_date: Optional[datetime] = None
    provider_name: Optional[str] = None
    clinic_location: Optional[str] = None
    appointment_description: Optional[str] = None
    patient_type: str = "new"
    status: str
    intake_link_token: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Forms ─────────────────────────────────────────────────────────────────────

class FormStatus(BaseModel):
    """Flattened view of a patient_form + its form_definition."""
    id: uuid.UUID           # patient_form.id (used in API calls to update status / save fields)
    form_id: str            # form_definition.id  e.g. 'brief_i693'
    title: str
    description: Optional[str] = None
    category: str
    status: str             # not_started | in_progress | completed
    is_required: bool
    estimated_minutes: Optional[int] = None
    sort_order: int
    file_template: Optional[str] = None

    model_config = {"from_attributes": True}


class PatientFormUpdate(BaseModel):
    status: Optional[str] = None          # not_started | in_progress | completed
    intake_method: Optional[str] = None   # ai | manual
    file_path: Optional[str] = None


class FieldValueIn(BaseModel):
    field_id: str
    field_value: str
    collection_method: Optional[str] = "ai_chat"


class FieldsUpsert(BaseModel):
    fields: List[FieldValueIn]


class FieldValueOut(BaseModel):
    field_id: str
    field_value: Optional[str]
    collected_at: datetime
    collection_method: Optional[str]


# ── Intake context (returned by /intake/{token}) ─────────────────────────────

class IntakeContext(BaseModel):
    patient: PatientOut
    appointment: AppointmentOut
    forms: List[FormStatus]


# ── Clinic portal views ───────────────────────────────────────────────────────

class AppointmentSummary(BaseModel):
    """Appointment enriched with patient name + form counts — for clinic list."""
    id: uuid.UUID
    patient_id: uuid.UUID
    patient_name: str
    patient_email: Optional[str] = None
    patient_phone: Optional[str] = None
    appointment_type: str
    appointment_date: Optional[datetime] = None
    provider_name: Optional[str] = None
    clinic_location: Optional[str] = None
    appointment_description: Optional[str] = None
    patient_type: str = "new"
    status: str
    intake_link_token: str
    forms_total: int = 0
    forms_completed: int = 0


class ReminderResult(BaseModel):
    email_sent: bool
    sms_sent: bool
    remaining: int
    message: str


class PatientSummary(BaseModel):
    """Patient enriched with appointment stats — for clinic patient list."""
    id: uuid.UUID
    full_name: str
    first_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    appointment_count: int = 0
    last_appointment_date: Optional[datetime] = None
    # Next upcoming appointment (for reminder button)
    next_appointment_id: Optional[uuid.UUID] = None
    next_appointment_date: Optional[datetime] = None
    next_appointment_type: Optional[str] = None
    next_forms_total: int = 0
    next_forms_completed: int = 0
    next_intake_token: Optional[str] = None

    model_config = {"from_attributes": True}
