"""
Seeds AlanBehrman form definitions and creates one demo intake.

Run from elevia-AlanBehrman/:
    python service/seed.py
"""
import os
import sys
from datetime import datetime, timezone, date

from sqlalchemy import delete

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from service.database import engine, SessionLocal
from service import models, crud, schemas


LEGACY_FORM_IDS = [
    "brief_i693",
    "full_intake",
    "update",
    "uscis_release",
    "flu_vaccine_consent",
    "electronic_comms_consent",
    "vaccine",
    "id_verify",
    "interpreter",
]


FORM_DEFINITIONS = [
    models.FormDefinition(
        id="client_info",
        title="Client Information",
        description="Client demographics, contact details, emergency contact, and care preferences.",
        appointment_types=None,
        category="required",
        is_required=True,
        estimated_minutes=4,
        sort_order=1,
    ),
    models.FormDefinition(
        id="credit_card_authorization",
        title="Credit Card Authorization",
        description="Step One billing authorization with cardholder, billing address, card type, card number, expiration, CVC, and authorization signature.",
        appointment_types=None,
        category="required",
        is_required=True,
        estimated_minutes=3,
        sort_order=2,
    ),
    models.FormDefinition(
        id="hipaa",
        title="HIPAA",
        description="Local AlanBehrman HIPAA notice replica with name, email, date, and e-signature fields.",
        appointment_types=None,
        category="consent",
        is_required=True,
        estimated_minutes=2,
        sort_order=3,
    ),
    models.FormDefinition(
        id="provider_consent",
        title="Provider-Specific Informed Consent",
        description="Step Three informed consent selected dynamically from the chosen AlanBehrman provider.",
        appointment_types=None,
        category="consent",
        is_required=True,
        estimated_minutes=4,
        sort_order=4,
    ),
    models.FormDefinition(
        id="cancellation_policy",
        title="Cancellation Policy",
        description="Step Three cancellation policy acknowledgement.",
        appointment_types=None,
        category="consent",
        is_required=True,
        estimated_minutes=1,
        sort_order=5,
    ),
    models.FormDefinition(
        id="insurance_authorization",
        title="Insurance Authorization",
        description="Step Four insurance authorization for payer communication and benefit verification.",
        appointment_types=None,
        category="consent",
        is_required=False,
        estimated_minutes=3,
        sort_order=6,
    ),
    models.FormDefinition(
        id="surprise_billing",
        title="Surprise Billing Policy",
        description="Step Four billing disclosure acknowledgement.",
        appointment_types=None,
        category="consent",
        is_required=True,
        estimated_minutes=1,
        sort_order=7,
    ),
    models.FormDefinition(
        id="release_information",
        title="Consent & Authorization to Release Information",
        description="Optional authorization for care coordination with another person or organization.",
        appointment_types=None,
        category="optional",
        is_required=False,
        estimated_minutes=3,
        sort_order=8,
    ),
    models.FormDefinition(
        id="relational_intake",
        title="Relational Therapy Initial Intake Form",
        description="Added when relationship, couples, marriage, or family concerns are expressed.",
        appointment_types=None,
        category="required",
        is_required=False,
        estimated_minutes=5,
        sort_order=9,
    ),
    models.FormDefinition(
        id="coaching_consent",
        title="Coaching Informed Consent",
        description="Added when coaching, career, leadership, or life goal concerns are expressed.",
        appointment_types=None,
        category="consent",
        is_required=False,
        estimated_minutes=2,
        sort_order=10,
    ),
    models.FormDefinition(
        id="phq9",
        title="PHQ-9 Depression Screening",
        description="9-item Patient Health Questionnaire served only when depression or mood concerns are expressed.",
        appointment_types=None,
        category="required",
        is_required=True,
        estimated_minutes=2,
        sort_order=11,
        file_template="Knowledge/forms/phq9_rag_elevia.md",
    ),
    models.FormDefinition(
        id="gad7",
        title="GAD-7 Anxiety Screening",
        description="7-item Generalized Anxiety Disorder questionnaire served only when anxiety concerns are expressed.",
        appointment_types=None,
        category="required",
        is_required=True,
        estimated_minutes=2,
        sort_order=12,
        file_template="Knowledge/forms/gad7_rag_elevia.md",
    ),
]


def upsert_form_definition(db, form):
    existing = db.get(models.FormDefinition, form.id)
    if not existing:
        db.add(form)
        return "inserted"

    for field in [
        "title",
        "description",
        "appointment_types",
        "category",
        "is_required",
        "estimated_minutes",
        "sort_order",
        "file_template",
    ]:
        setattr(existing, field, getattr(form, field))
    return "updated"


def seed():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    db.execute(delete(models.PatientForm).where(models.PatientForm.form_id.in_(LEGACY_FORM_IDS)))
    db.execute(delete(models.FormDefinition).where(models.FormDefinition.id.in_(LEGACY_FORM_IDS)))
    db.commit()

    inserted = 0
    updated = 0
    for form in FORM_DEFINITIONS:
        result = upsert_form_definition(db, form)
        inserted += result == "inserted"
        updated += result == "updated"
    db.commit()
    print(f"AlanBehrman form definitions: {inserted} inserted, {updated} updated")

    patient = crud.create_patient(db, schemas.PatientCreate(
        full_name="Avery Johnson",
        first_name="Avery",
        dob=date(1990, 7, 14),
        gender="Female",
        email="avery.johnson@example.com",
        phone="(404) 555-0188",
    ))
    print(f"Demo client created: {patient.full_name}")
    print(f"Client GUID: {patient.id}")

    appt = crud.create_appointment(db, schemas.AppointmentCreate(
        patient_id=patient.id,
        appointment_type="therapy_consultation",
        appointment_date=datetime(2026, 5, 21, 19, 30, tzinfo=timezone.utc),
        provider_name="Meredith Mitchell, PMHNP-BC",
        clinic_location="Marietta, GA",
        appointment_description="New client intake for anxiety, panic symptoms, low mood, and medication management questions.",
    ))
    print(f"Appointment created: {appt.appointment_type}")
    print(f"Appointment ID: {appt.id}")
    print(f"Intake token: {appt.intake_link_token}")

    from sqlalchemy import select
    rows = db.execute(
        select(models.PatientForm, models.FormDefinition)
        .join(models.FormDefinition)
        .where(models.PatientForm.appointment_id == appt.id)
        .order_by(models.FormDefinition.sort_order)
    ).all()
    print(f"\nAssigned {len(rows)} forms:")
    for patient_form, form_def in rows:
        req = "required" if form_def.is_required else "optional"
        print(f"  [{form_def.category:8s}] {patient_form.form_id:28s} {form_def.title} ({req})")

    print("\nOpen the intake flow:")
    print(f"  http://localhost:8025/?t={appt.intake_link_token}")

    db.close()


if __name__ == "__main__":
    seed()
