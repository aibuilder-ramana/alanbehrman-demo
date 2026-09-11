from __future__ import annotations
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from service import models, schemas


def _now():
    return datetime.now(timezone.utc)


# ── Conditional screener keywords ─────────────────────────────────────────────

_DEPRESSION_KW = [
    'depress', 'sad', 'hopeless', 'anhedoni', 'suicid', 'worthless',
    'low mood', 'mdd', 'dysthymi', 'tearful', 'melanchol', 'grief',
    'crying', 'joyless', 'loss of interest', 'phq',
]
_ANXIETY_KW = [
    'anxi', 'panic', 'worr', 'gad', 'nervou', 'phobia', 'ptsd',
    'trauma', 'hyperventil', 'palpitat', 'restless', 'fear', 'dread',
    'stress', 'tense', 'tension',
]
_RELATIONAL_KW = [
    'couple', 'partner', 'marriage', 'marital', 'relationship', 'family',
    'relational',
]
_COACHING_KW = [
    'coach', 'coaching', 'career', 'leadership', 'executive', 'life goal',
    'goal',
]
_RELEASE_KW = [
    'release', 'records', 'coordinate', 'school', 'attorney', 'court',
    'doctor', 'physician', 'psychiatrist',
]


def _desc_matches(desc: str, keywords: list) -> bool:
    if not desc:
        return False
    d = desc.lower()
    return any(kw in d for kw in keywords)


def _get_patient_type(db: Session, patient_id: uuid.UUID) -> str:
    """Classify patient as new / returning_recent (< 3 yrs) / returning_stale (≥ 3 yrs)."""
    prior_dates = db.execute(
        select(models.Appointment.created_at)
        .where(
            models.Appointment.patient_id == patient_id,
            models.Appointment.status != 'cancelled',
        )
    ).scalars().all()

    if not prior_dates:
        return 'new'

    most_recent = max(prior_dates)
    # Ensure tz-aware comparison
    if most_recent.tzinfo is None:
        most_recent = most_recent.replace(tzinfo=timezone.utc)
    cutoff = _now() - timedelta(days=3 * 365)
    return 'returning_recent' if most_recent >= cutoff else 'returning_stale'


# ── Patients ──────────────────────────────────────────────────────────────────

def create_patient(db: Session, data: schemas.PatientCreate) -> models.Patient:
    patient = models.Patient(**data.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: uuid.UUID) -> Optional[models.Patient]:
    return db.get(models.Patient, patient_id)


def update_patient(db: Session, patient_id: uuid.UUID, data: schemas.PatientUpdate) -> Optional[models.Patient]:
    p = db.get(models.Patient, patient_id)
    if not p:
        return None
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


# ── Appointments ──────────────────────────────────────────────────────────────

def create_appointment(db: Session, data: schemas.AppointmentCreate) -> models.Appointment:
    # Determine patient type BEFORE adding this appointment
    patient_type = _get_patient_type(db, data.patient_id)

    token = str(uuid.uuid4())
    appt = models.Appointment(
        **data.model_dump(),
        intake_link_token=token,
        patient_type=patient_type,
    )
    db.add(appt)
    db.flush()  # get appt.id before creating patient_forms

    # Description-driven screener flags
    desc = data.appointment_description or ''
    needs_phq9 = _desc_matches(desc, _DEPRESSION_KW)
    needs_gad7  = _desc_matches(desc, _ANXIETY_KW)
    needs_relational = _desc_matches(desc, _RELATIONAL_KW)
    needs_coaching = _desc_matches(desc, _COACHING_KW)
    needs_release = _desc_matches(desc, _RELEASE_KW)

    # All form definitions, sorted
    all_forms = db.execute(
        select(models.FormDefinition).order_by(models.FormDefinition.sort_order)
    ).scalars().all()

    for f in all_forms:
        # Appointment-type filter (skip forms restricted to other visit types)
        if f.id != 'update' and f.appointment_types and data.appointment_type not in f.appointment_types:
            continue

        # Conditional AlanBehrman packet items.
        if f.id == 'phq9' and not needs_phq9:
            continue
        if f.id == 'gad7' and not needs_gad7:
            continue
        if f.id == 'relational_intake' and not needs_relational:
            continue
        if f.id == 'coaching_consent' and not needs_coaching:
            continue
        if f.id == 'release_information' and not needs_release:
            continue

        db.add(models.PatientForm(
            patient_id=data.patient_id,
            appointment_id=appt.id,
            form_id=f.id,
        ))

    db.commit()
    db.refresh(appt)
    return appt


def get_appointment(db: Session, appointment_id: uuid.UUID) -> Optional[models.Appointment]:
    return db.get(models.Appointment, appointment_id)


def get_appointment_by_token(db: Session, token: str) -> Optional[models.Appointment]:
    return db.execute(
        select(models.Appointment).where(models.Appointment.intake_link_token == token)
    ).scalar_one_or_none()


# ── Forms ─────────────────────────────────────────────────────────────────────

def get_forms_for_appointment(db: Session, appointment_id: uuid.UUID):
    """Returns list of (PatientForm, FormDefinition) tuples ordered by sort_order."""
    return db.execute(
        select(models.PatientForm, models.FormDefinition)
        .join(models.FormDefinition, models.PatientForm.form_id == models.FormDefinition.id)
        .where(models.PatientForm.appointment_id == appointment_id)
        .order_by(models.FormDefinition.sort_order)
    ).all()


def update_patient_form(
    db: Session,
    patient_form_id: uuid.UUID,
    data: schemas.PatientFormUpdate,
) -> Optional[models.PatientForm]:
    pf = db.get(models.PatientForm, patient_form_id)
    if not pf:
        return None

    updates = data.model_dump(exclude_none=True)

    if updates.get("status") == "in_progress" and not pf.started_at:
        pf.started_at = _now()

    if updates.get("status") == "completed":
        pf.completed_at = _now()
        # ensure data directory exists for this patient
        patient_dir = os.path.join("data", str(pf.patient_id))
        os.makedirs(patient_dir, exist_ok=True)

    for k, v in updates.items():
        setattr(pf, k, v)

    db.commit()
    db.refresh(pf)
    return pf


def upsert_field_values(
    db: Session,
    patient_form_id: uuid.UUID,
    fields: List[schemas.FieldValueIn],
) -> bool:
    pf = db.get(models.PatientForm, patient_form_id)
    if not pf:
        return False

    # auto-advance status to in_progress on first field save
    if pf.status == "not_started":
        pf.status = "in_progress"
        pf.started_at = _now()

    for f in fields:
        existing = db.execute(
            select(models.FormFieldValue).where(
                models.FormFieldValue.patient_form_id == patient_form_id,
                models.FormFieldValue.field_id == f.field_id,
            )
        ).scalar_one_or_none()

        if existing:
            existing.field_value = f.field_value
            existing.collected_at = _now()
        else:
            db.add(models.FormFieldValue(
                patient_form_id=patient_form_id,
                field_id=f.field_id,
                field_value=f.field_value,
                collection_method=f.collection_method,
            ))

    db.commit()
    return True


def get_field_values(db: Session, patient_form_id: uuid.UUID) -> List[models.FormFieldValue]:
    return db.execute(
        select(models.FormFieldValue)
        .where(models.FormFieldValue.patient_form_id == patient_form_id)
        .order_by(models.FormFieldValue.collected_at)
    ).scalars().all()


# ── Clinic portal queries ─────────────────────────────────────────────────────

def list_patients(
    db: Session, q: Optional[str] = None, limit: int = 200
) -> List[models.Patient]:
    stmt = select(models.Patient).where(models.Patient.is_active == True)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                models.Patient.full_name.ilike(like),
                models.Patient.email.ilike(like),
                models.Patient.phone.ilike(like),
            )
        )
    return db.execute(stmt.order_by(models.Patient.created_at.desc()).limit(limit)).scalars().all()


def list_patients_with_stats(
    db: Session, q: Optional[str] = None, limit: int = 200
) -> List[schemas.PatientSummary]:
    patients = list_patients(db, q, limit)
    result = []
    for p in patients:
        appts = db.execute(
            select(models.Appointment)
            .where(
                models.Appointment.patient_id == p.id,
                models.Appointment.status != "cancelled",
            )
            .order_by(models.Appointment.appointment_date.desc())
        ).scalars().all()

        # Find the nearest upcoming appointment (regardless of form completion —
        # a fully-completed appointment should still surface here, just with
        # zero pending forms, rather than disappear from the registry).
        next_appt = None
        next_forms_total = 0
        next_forms_completed = 0
        for a in sorted(appts, key=lambda x: x.appointment_date or _now()):
            if a.appointment_date and a.appointment_date >= _now():
                form_rows = db.execute(
                    select(models.PatientForm)
                    .where(models.PatientForm.appointment_id == a.id)
                ).scalars().all()
                next_appt = a
                next_forms_total = len(form_rows)
                next_forms_completed = sum(1 for f in form_rows if f.status == "completed")
                break

        ref_appt = next_appt or (appts[0] if appts else None)
        provider_name = ref_appt.provider_name if ref_appt else None
        clinic_location = ref_appt.clinic_location if ref_appt else None

        result.append(schemas.PatientSummary(
            id=p.id,
            full_name=p.full_name,
            first_name=p.first_name,
            dob=p.dob,
            gender=p.gender,
            email=p.email,
            phone=p.phone,
            created_at=p.created_at,
            appointment_count=len(appts),
            last_appointment_date=appts[0].appointment_date if appts else None,
            next_appointment_id=next_appt.id if next_appt else None,
            next_appointment_date=next_appt.appointment_date if next_appt else None,
            next_appointment_type=next_appt.appointment_type if next_appt else None,
            next_forms_total=next_forms_total,
            next_forms_completed=next_forms_completed,
            next_intake_token=next_appt.intake_link_token if next_appt else None,
            provider_name=provider_name,
            clinic_location=clinic_location,
        ))
    return result


# ── Clinical notes ────────────────────────────────────────────────────────────

def list_clinical_notes(db: Session, patient_id: uuid.UUID) -> List[models.ClinicalNote]:
    return db.execute(
        select(models.ClinicalNote)
        .where(models.ClinicalNote.patient_id == patient_id)
        .order_by(models.ClinicalNote.encounter_date.desc())
    ).scalars().all()


def list_upcoming_appointments(
    db: Session, limit: int = 200
) -> List[schemas.AppointmentSummary]:
    rows = db.execute(
        select(models.Appointment, models.Patient)
        .join(models.Patient, models.Appointment.patient_id == models.Patient.id)
        .where(
            or_(
                models.Appointment.appointment_date >= _now(),
                models.Appointment.appointment_date.is_(None),
            ),
            models.Appointment.status != "cancelled",
        )
        .order_by(
            models.Appointment.appointment_date.is_(None),  # NULLs last
            models.Appointment.appointment_date,
        )
        .limit(limit)
    ).all()

    result = []
    for appt, patient in rows:
        form_rows = db.execute(
            select(models.PatientForm).where(models.PatientForm.appointment_id == appt.id)
        ).scalars().all()
        result.append(schemas.AppointmentSummary(
            id=appt.id,
            patient_id=appt.patient_id,
            patient_name=patient.full_name,
            patient_email=patient.email,
            patient_phone=patient.phone,
            appointment_type=appt.appointment_type,
            appointment_date=appt.appointment_date,
            provider_name=appt.provider_name,
            clinic_location=appt.clinic_location,
            appointment_description=appt.appointment_description,
            patient_type=appt.patient_type,
            status=appt.status,
            intake_link_token=appt.intake_link_token,
            forms_total=len(form_rows),
            forms_completed=sum(1 for f in form_rows if f.status == "completed"),
        ))
    return result
