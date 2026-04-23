import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Date, DateTime, Integer,
    ForeignKey, Text, UniqueConstraint, Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from service.database import Base


def _now():
    return datetime.now(timezone.utc)


class Patient(Base):
    __tablename__ = "patients"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name  = Column(String(255), nullable=False)
    first_name = Column(String(100))
    dob        = Column(Date)
    gender     = Column(String(20))
    email      = Column(String(255))
    phone      = Column(String(30))
    created_at = Column(DateTime(timezone=True), default=_now)
    is_active  = Column(Boolean, default=True)

    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")


class Appointment(Base):
    __tablename__ = "appointments"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id        = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    appointment_type  = Column(String(100), nullable=False)
    appointment_date  = Column(DateTime(timezone=True))
    provider_name     = Column(String(255))
    clinic_location   = Column(String(255))
    appointment_description = Column(Text)
    patient_type      = Column(String(30), nullable=False, default="new")  # new | returning_recent | returning_stale
    status            = Column(String(30), nullable=False, default="scheduled")
    intake_link_token = Column(String(255), unique=True, nullable=False)
    created_at        = Column(DateTime(timezone=True), default=_now)

    patient       = relationship("Patient", back_populates="appointments")
    patient_forms = relationship("PatientForm", back_populates="appointment", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_appt_token", "intake_link_token"),)


class FormDefinition(Base):
    """Master reference — which forms exist. Seeded once."""
    __tablename__ = "form_definitions"

    id                = Column(String(50), primary_key=True)
    title             = Column(String(255), nullable=False)
    description       = Column(Text)
    appointment_types = Column(ARRAY(String))   # NULL = applies to all appointment types
    category          = Column(String(30), nullable=False)  # required | consent | optional
    is_required       = Column(Boolean, nullable=False, default=True)
    estimated_minutes = Column(Integer)
    sort_order        = Column(Integer, nullable=False, default=0)
    file_template     = Column(String(512))     # relative path to PDF template


class PatientForm(Base):
    """One row per (patient, appointment, form). Core tracking table."""
    __tablename__ = "patient_forms"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id     = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False)
    form_id        = Column(String(50), ForeignKey("form_definitions.id"), nullable=False)
    status         = Column(String(30), nullable=False, default="not_started")  # not_started | in_progress | completed
    intake_method  = Column(String(20))   # ai | manual
    started_at     = Column(DateTime(timezone=True))
    completed_at   = Column(DateTime(timezone=True))
    file_path      = Column(String(512))  # relative: data/<patient_guid>/<form_id>_<appt_id>.pdf
    created_at     = Column(DateTime(timezone=True), default=_now)

    appointment  = relationship("Appointment", back_populates="patient_forms")
    form_def     = relationship("FormDefinition")
    field_values = relationship("FormFieldValue", back_populates="patient_form", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("patient_id", "appointment_id", "form_id", name="uq_patient_appt_form"),
        Index("idx_pf_appointment", "appointment_id"),
    )


class FormFieldValue(Base):
    """Individual field values captured during AI chat or manual fill."""
    __tablename__ = "form_field_values"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_form_id   = Column(UUID(as_uuid=True), ForeignKey("patient_forms.id", ondelete="CASCADE"), nullable=False)
    field_id          = Column(String(100), nullable=False)
    field_value       = Column(Text)
    collected_at      = Column(DateTime(timezone=True), default=_now)
    collection_method = Column(String(20))  # ai_chat | manual

    patient_form = relationship("PatientForm", back_populates="field_values")

    __table_args__ = (
        UniqueConstraint("patient_form_id", "field_id", name="uq_form_field"),
        Index("idx_ffv_patient_form", "patient_form_id"),
    )


class IntakeSession(Base):
    """Full AI chat transcript per session — audit trail."""
    __tablename__ = "intake_sessions"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id     = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False)
    started_at     = Column(DateTime(timezone=True), default=_now)
    completed_at   = Column(DateTime(timezone=True))
    messages       = Column(JSONB, nullable=False, default=list)
