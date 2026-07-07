"""
Fills in (or leaves untouched) intake forms on each synthetic patient's
upcoming appointment so the Patient Registry shows a realistic mix of
states: fully completed, partially filled/in-progress, and not started —
instead of every patient showing 0/N forms done.

Run AFTER seed_synthetic_patients.py and seed_upcoming_appointments.py,
from elevia-AlanBehrman/:
    python service/seed_form_progress.py
"""
import os
import sys
from datetime import datetime, timezone, timedelta

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from sqlalchemy import select

from service.database import engine, SessionLocal
from service import models, crud, schemas

# Synthetic field values per form_id, keyed by the AlanBehrman form catalog
# (service/seed.py FORM_DEFINITIONS). Field ids are free-text and only need
# to be internally consistent — there's no fixed schema enforced beyond that.
def field_values_for(form_id: str, patient_name: str, provider_name: str):
    first = patient_name.split(" ")[0]
    if form_id == "client_info":
        return [
            ("full_name", patient_name),
            ("date_of_birth", "on file"),
            ("address", f"{100 + len(patient_name)} Maple Street, Marietta, GA 30060"),
            ("phone", "on file"),
            ("email", "on file"),
            ("emergency_contact_name", f"{first}'s emergency contact"),
            ("emergency_contact_phone", "(404) 555-0199"),
        ]
    if form_id == "credit_card_authorization":
        return [
            ("cardholder_name", patient_name),
            ("billing_zip", "30060"),
            ("card_type", "Visa"),
            ("card_last4", "4242"),
            ("expiration", "09/28"),
            ("signature", patient_name),
        ]
    if form_id == "hipaa":
        return [
            ("acknowledged", "true"),
            ("signature", patient_name),
        ]
    if form_id == "provider_consent":
        return [
            ("provider_name", provider_name),
            ("acknowledged", "true"),
            ("signature", patient_name),
        ]
    if form_id == "cancellation_policy":
        return [
            ("acknowledged", "true"),
            ("signature", patient_name),
        ]
    if form_id == "insurance_authorization":
        return [
            ("insurance_carrier", "BlueCross BlueShield of Georgia"),
            ("member_id", f"BCBS{abs(hash(patient_name)) % 90000 + 10000}"),
            ("group_number", "GA-44210"),
            ("signature", patient_name),
        ]
    if form_id == "surprise_billing":
        return [
            ("acknowledged", "true"),
            ("signature", patient_name),
        ]
    if form_id == "phq9":
        return [
            ("total_score", "9"),
            ("severity", "Mild"),
            ("q9_suicidal_ideation", "Not at all"),
        ]
    if form_id == "gad7":
        return [
            ("total_score", "8"),
            ("severity", "Mild"),
        ]
    return [("acknowledged", "true"), ("signature", patient_name)]


# Per-patient (by email) target state for their upcoming appointment's forms:
#   "completed"    — every form filled in and marked completed
#   "partial"      — a mix of completed / in_progress / not_started
#   "not_started"  — left untouched (the default)
PATIENT_STATES = {
    "maria.gonzalez@example.com":   "completed",
    "james.whitfield@example.com":  "completed",
    "aisha.thompson@example.com":   "partial",
    "daniel.kim@example.com":       "partial",
    "olivia.bennett@example.com":   "partial",
    "marcus.reed@example.com":      "partial",
    "priya.natarajan@example.com":  "completed",
    "ethan.caldwell@example.com":   "not_started",
    "sofia.alvarez@example.com":    "not_started",
    "nathaniel.brooks@example.com": "not_started",

    # 10 patients seeded separately in service/seed.py under Dr. Patty Postanowicz
    "grace.nguyen@example.com":     "completed",
    "marcus.bell@example.com":      "completed",
    "isabella.cruz@example.com":    "completed",
    "ethan.rivera@example.com":     "partial",
    "ava.thompson@example.com":     "partial",
    "noah.patel@example.com":       "partial",
    "sofia.ramirez@example.com":    "partial",
    "liam.brooks@example.com":      "not_started",
    "jordan.alvarez@example.com":   "not_started",
    "maya.chen@example.com":        "not_started",

    # Original demo patient from service/seed.py — her only appointment is in
    # the past, so we also give her a fresh upcoming one (see ensure step below).
    "avery.johnson@example.com":    "partial",
}


def ensure_upcoming_appointment(db, patient):
    """Avery Johnson's only appointment is May 2026 (now in the past) — give
    her a future one too, so she shows up in the registry like everyone else."""
    has_upcoming = db.execute(
        select(models.Appointment).where(
            models.Appointment.patient_id == patient.id,
            models.Appointment.appointment_date >= datetime.now(timezone.utc),
        )
    ).scalar_one_or_none()
    if has_upcoming:
        return

    last_appt = db.execute(
        select(models.Appointment)
        .where(models.Appointment.patient_id == patient.id)
        .order_by(models.Appointment.appointment_date.desc())
    ).scalars().first()

    crud.create_appointment(db, schemas.AppointmentCreate(
        patient_id=patient.id,
        appointment_type="therapy_consultation",
        appointment_date=datetime.now(timezone.utc) + timedelta(days=5),
        provider_name=last_appt.provider_name if last_appt else None,
        clinic_location=last_appt.clinic_location if last_appt else "Marietta, GA",
        appointment_description="Follow-up medication management for anxiety, panic symptoms, and low mood.",
    ))
    db.commit()
    print(f"Created upcoming appointment for {patient.full_name} (had none)")


def seed():
    db = SessionLocal()

    for email, target_state in PATIENT_STATES.items():
        patient = db.execute(
            select(models.Patient).where(models.Patient.email == email)
        ).scalar_one_or_none()
        if not patient:
            print(f"Skipping (not found): {email}")
            continue

        ensure_upcoming_appointment(db, patient)

        upcoming_appt = db.execute(
            select(models.Appointment)
            .where(models.Appointment.patient_id == patient.id)
            .order_by(models.Appointment.appointment_date.desc())
        ).scalars().first()
        if not upcoming_appt:
            continue

        form_rows = crud.get_forms_for_appointment(db, upcoming_appt.id)
        if not form_rows:
            print(f"No forms attached for {patient.full_name} — run seed.py first")
            continue

        if target_state == "not_started":
            print(f"{patient.full_name}: left not started ({len(form_rows)} forms)")
            continue

        # "partial" completes roughly the first half, puts one form in progress,
        # and leaves the rest untouched. "completed" finishes all of them.
        completed_count = 0
        for i, (pf, fd) in enumerate(form_rows):
            values = field_values_for(fd.id, patient.full_name, upcoming_appt.provider_name)

            if target_state == "completed":
                crud.upsert_field_values(db, pf.id, [
                    schemas.FieldValueIn(field_id=k, field_value=v, collection_method="manual")
                    for k, v in values
                ])
                crud.update_patient_form(db, pf.id, schemas.PatientFormUpdate(status="completed"))
                completed_count += 1

            elif target_state == "partial":
                half = len(form_rows) // 2
                if i < half:
                    crud.upsert_field_values(db, pf.id, [
                        schemas.FieldValueIn(field_id=k, field_value=v, collection_method="manual")
                        for k, v in values
                    ])
                    crud.update_patient_form(db, pf.id, schemas.PatientFormUpdate(status="completed"))
                    completed_count += 1
                elif i == half:
                    # One form left partially filled — in progress, not complete.
                    crud.upsert_field_values(db, pf.id, [
                        schemas.FieldValueIn(field_id=values[0][0], field_value=values[0][1], collection_method="manual")
                    ])
                # else: left not_started

        print(f"{patient.full_name}: {target_state} — {completed_count}/{len(form_rows)} forms completed")

    db.close()


if __name__ == "__main__":
    seed()
