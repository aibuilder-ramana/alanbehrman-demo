"""
Seeds one upcoming (future-dated) appointment for each of the 10 synthetic
patients created by seed_synthetic_patients.py. Each appointment keeps the
patient's existing provider assignment (Dr. Ramakanth Vemuluri or Meredith
Mitchell) so charts stay consistent, and picks up the standard AlanBehrman
form packet automatically (creating pending forms for the Patient Registry's
"Pending Forms" column and enabling the Reminder button).

These appointments are what the provider Dashboard > Schedules view reads
from GET /api/appointments/upcoming.

Run from elevia-AlanBehrman/:
    python service/seed_upcoming_appointments.py
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

SYNTHETIC_EMAILS = [
    "maria.gonzalez@example.com",
    "james.whitfield@example.com",
    "aisha.thompson@example.com",
    "daniel.kim@example.com",
    "olivia.bennett@example.com",
    "marcus.reed@example.com",
    "priya.natarajan@example.com",
    "ethan.caldwell@example.com",
    "sofia.alvarez@example.com",
    "nathaniel.brooks@example.com",
]

CLINIC_LOCATIONS = ["Marietta, GA", "Alpharetta, GA — Telehealth"]

# Follow-up concern per patient, aligned with each patient's original visit.
FOLLOWUP_DESCRIPTIONS = [
    "Follow-up for generalized anxiety disorder; reviewing relaxation technique progress.",
    "Follow-up medication management for major depressive disorder.",
    "Follow-up for work-related stress and anxiety; reviewing coping strategies.",
    "Follow-up ADHD medication management; reviewing titration response.",
    "Follow-up for grief and low mood following recent loss.",
    "Follow-up for generalized anxiety disorder and sleep concerns.",
    "Follow-up for panic disorder and health anxiety.",
    "Follow-up medication check for major depressive disorder.",
    "Follow-up for adjustment disorder related to relationship transition.",
    "Follow-up for major depressive disorder; assessing SSRI response.",
]


def seed():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    created = 0
    for i, email in enumerate(SYNTHETIC_EMAILS):
        patient = db.execute(
            select(models.Patient).where(models.Patient.email == email)
        ).scalar_one_or_none()
        if not patient:
            print(f"Skipping (not found): {email}")
            continue

        # Reuse the provider + location from the patient's most recent appointment.
        last_appt = db.execute(
            select(models.Appointment)
            .where(models.Appointment.patient_id == patient.id)
            .order_by(models.Appointment.appointment_date.desc())
        ).scalars().first()

        provider_name = last_appt.provider_name if last_appt else None
        clinic_location = last_appt.clinic_location if last_appt else CLINIC_LOCATIONS[i % len(CLINIC_LOCATIONS)]

        appt_date = datetime.now(timezone.utc) + timedelta(days=3 + i * 4, hours=(i % 6))

        # Dr. Vemuluri sees patients for psychiatry consultations; Mitchell for therapy.
        appt_type = "psychiatry_consultation" if provider_name and "Vemuluri" in provider_name else "therapy_consultation"

        appt = crud.create_appointment(db, schemas.AppointmentCreate(
            patient_id=patient.id,
            appointment_type=appt_type,
            appointment_date=appt_date,
            provider_name=provider_name,
            clinic_location=clinic_location,
            appointment_description=FOLLOWUP_DESCRIPTIONS[i],
        ))

        created += 1
        print(f"Upcoming appointment: {patient.full_name}  →  {provider_name}  →  {appt_date.strftime('%Y-%m-%d %H:%M UTC')}")

    print(f"\n{created} upcoming appointments created.")
    db.close()


if __name__ == "__main__":
    seed()
