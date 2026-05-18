"""
Seeds form_definitions and creates a demo patient + appointment.

Run from elevia-alanbehrman/:
    python service/seed.py
"""
import os
import sys
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from service.database import engine, SessionLocal
from service import models, crud, schemas


FORM_DEFINITIONS = [
    # ── Real clinic forms from resources/sampleforms/pdfs/ ─────────────────
    models.FormDefinition(
        id="brief_i693",
        title="Brief I-693 Form",
        description="Condensed USCIS immigration medical examination form (I-693). Required for adjustment of status.",
        appointment_types=["immigration_medical_exam"],
        category="required",
        is_required=True,
        estimated_minutes=4,
        sort_order=1,
        file_template="resources/sampleforms/pdfs/BRIEFI693_English_04182026.docx.pdf",
    ),
    models.FormDefinition(
        id="full_intake",
        title="Medical Full Intake Form",
        description="Comprehensive medical history including conditions, medications, allergies, surgical history, and social history.",
        appointment_types=None,   # applies to all appointment types
        category="required",
        is_required=True,
        estimated_minutes=8,
        sort_order=2,
        file_template="Knowledge/forms/full_intake_rag_elevia.md",
    ),
    models.FormDefinition(
        id="update",
        title="Patient Update Form",
        description="Update to existing medical records — changes in medications, conditions, or contact information since your last visit.",
        appointment_types=None,
        category="required",
        is_required=False,
        estimated_minutes=3,
        sort_order=3,
        file_template="Knowledge/forms/update_rag_elevia.md",
    ),
    # ── Supporting forms ────────────────────────────────────────────────────
    models.FormDefinition(
        id="vaccine",
        title="Vaccination Record",
        description="Upload or enter your immunization history (MMR, Tdap, COVID-19, Flu).",
        appointment_types=None,
        category="required",
        is_required=True,
        estimated_minutes=3,
        sort_order=4,
    ),
    models.FormDefinition(
        id="id_verify",
        title="Photo ID Verification",
        description="Upload a passport, green card, or state-issued photo ID.",
        appointment_types=None,
        category="required",
        is_required=True,
        estimated_minutes=2,
        sort_order=5,
    ),
    models.FormDefinition(
        id="hipaa",
        title="HIPAA Privacy Notice",
        description="Acknowledge receipt of our Notice of Privacy Practices.",
        appointment_types=None,
        category="consent",
        is_required=True,
        estimated_minutes=1,
        sort_order=6,
    ),
    models.FormDefinition(
        id="uscis_release",
        title="USCIS Release of Medical Information",
        description="Consent to share immigration medical exam results with USCIS.",
        appointment_types=["immigration_medical_exam"],
        category="consent",
        is_required=True,
        estimated_minutes=1,
        sort_order=7,
    ),
    models.FormDefinition(
        id="flu_vaccine_consent",
        title="Flu Vaccine Consent",
        description="Informed consent for seasonal influenza vaccination. Includes screening questions for contraindications and authorization to administer.",
        appointment_types=None,
        category="consent",
        is_required=True,
        estimated_minutes=2,
        sort_order=8,
        file_template="Knowledge/forms/flu_vaccine_consent_rag_elevia.md",
    ),
    models.FormDefinition(
        id="electronic_comms_consent",
        title="Electronic Communications Consent",
        description="Authorize 1 Stop Medical to contact you via text, phone, and email for appointment reminders, test results, and care coordination.",
        appointment_types=None,
        category="consent",
        is_required=True,
        estimated_minutes=1,
        sort_order=9,
        file_template="Knowledge/forms/electronic_communications_consent_rag_elevia.md",
    ),
    models.FormDefinition(
        id="phq9",
        title="PHQ-9 Depression Screening",
        description="9-item Patient Health Questionnaire for depression. Flags moderate-to-severe risk for clinical follow-up.",
        appointment_types=None,
        category="required",
        is_required=True,
        estimated_minutes=2,
        sort_order=10,
        file_template="Knowledge/forms/phq9_rag_elevia.md",
    ),
    models.FormDefinition(
        id="gad7",
        title="GAD-7 Anxiety Screening",
        description="7-item Generalized Anxiety Disorder questionnaire. Scores ≥10 trigger clinical review.",
        appointment_types=None,
        category="required",
        is_required=True,
        estimated_minutes=2,
        sort_order=11,
        file_template="Knowledge/forms/gad7_rag_elevia.md",
    ),
    models.FormDefinition(
        id="interpreter",
        title="Interpreter Request",
        description="Request a spoken-language interpreter for your appointment.",
        appointment_types=None,
        category="optional",
        is_required=False,
        estimated_minutes=1,
        sort_order=12,
    ),
]


def seed():
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # ── Form definitions ────────────────────────────────────────────────────
    inserted = 0
    for f in FORM_DEFINITIONS:
        if not db.get(models.FormDefinition, f.id):
            db.add(f)
            inserted += 1
    db.commit()
    print(f"✓ Form definitions: {inserted} inserted, {len(FORM_DEFINITIONS) - inserted} already existed")

    # ── Demo patient ────────────────────────────────────────────────────────
    from datetime import date
    patient = crud.create_patient(db, schemas.PatientCreate(
        full_name="Paranjit Kaur",
        first_name="Paranjit",
        dob=date(1991, 3, 12),
        gender="Female",
        email="paranjit.kaur@example.com",
        phone="(425) 555-0198",
    ))
    print(f"✓ Demo patient created: {patient.full_name}")
    print(f"  Patient GUID: {patient.id}")

    # ── Demo appointment ────────────────────────────────────────────────────
    appt = crud.create_appointment(db, schemas.AppointmentCreate(
        patient_id=patient.id,
        appointment_type="immigration_medical_exam",
        appointment_date=datetime(2026, 4, 22, 10, 30, tzinfo=timezone.utc),
        provider_name="Dr. Ramakanth Vemuluri, MD",
        clinic_location="Marietta, GA",
    ))
    print(f"✓ Appointment created: {appt.appointment_type}")
    print(f"  Appointment ID:  {appt.id}")
    print(f"  Intake token:    {appt.intake_link_token}")

    # Show assigned forms
    from sqlalchemy import select
    rows = db.execute(
        select(models.PatientForm, models.FormDefinition)
        .join(models.FormDefinition)
        .where(models.PatientForm.appointment_id == appt.id)
        .order_by(models.FormDefinition.sort_order)
    ).all()
    print(f"\n  Assigned {len(rows)} forms:")
    for pf, fd in rows:
        req = "required" if fd.is_required else "optional"
        print(f"    [{fd.category:8s}] {fd.id:15s}  {fd.title}  ({req})")

    print(f"\n{'─'*60}")
    print(f"🔗 Open the intake form:")
    print(f"   http://localhost:8025/?t={appt.intake_link_token}")
    print(f"{'─'*60}")

    db.close()


if __name__ == "__main__":
    seed()
