"""
Generates AlanBehrman synthetic clients and appointment links.

Run from elevia-AlanBehrman/:
    python service/gen_test_users.py
"""
import os
import sys
from datetime import datetime, timezone, timedelta, date

from sqlalchemy import delete

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from service.database import engine, SessionLocal
from service import models, crud, schemas
from service.seed import FORM_DEFINITIONS, LEGACY_FORM_IDS, upsert_form_definition

BASE_URL = "http://localhost:8025"


def ensure_alanbehrman_forms(db):
    db.execute(delete(models.PatientForm).where(models.PatientForm.form_id.in_(LEGACY_FORM_IDS)))
    db.execute(delete(models.FormDefinition).where(models.FormDefinition.id.in_(LEGACY_FORM_IDS)))
    for form in FORM_DEFINITIONS:
        upsert_form_definition(db, form)
    db.commit()


def make_patient(db, first, last, dob_year, dob_month, dob_day, gender, email, phone):
    return crud.create_patient(db, schemas.PatientCreate(
        full_name=f"{first} {last}",
        first_name=first,
        dob=date(dob_year, dob_month, dob_day),
        gender=gender,
        email=email,
        phone=phone,
    ))


def make_appointment(db, patient_id, days_from_now, provider, location, description):
    appt_date = datetime.now(timezone.utc) + timedelta(days=days_from_now)
    return crud.create_appointment(db, schemas.AppointmentCreate(
        patient_id=patient_id,
        appointment_type="therapy_consultation",
        appointment_date=appt_date,
        provider_name=provider,
        clinic_location=location,
        appointment_description=description,
    ))


def count_forms(db, appointment_id):
    rows = db.query(models.PatientForm).filter(models.PatientForm.appointment_id == appointment_id).all()
    total = len(rows)
    done = sum(1 for row in rows if row.status == "completed")
    form_ids = [row.form_id for row in rows]
    return total, done, form_ids


def run():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("\n" + "-" * 68)
    print("  Elevia AlanBehrman synthetic intake links")
    print("-" * 68)

    ensure_alanbehrman_forms(db)

    scenarios = [
        {
            "label": "Anxiety and panic -> GAD-7",
            "patient": ("Avery", "Johnson", 1990, 7, 14, "Female", "avery.johnson@example.com", "(404) 555-0188"),
            "provider": "Meredith Mitchell, PMHNP-BC",
            "location": "Marietta, GA",
            "description": "New client intake for anxiety, panic symptoms, stress, and medication management questions.",
        },
        {
            "label": "Depression and grief -> PHQ-9",
            "patient": ("Jordan", "Williams", 1994, 5, 8, "Female", "jordan.williams@example.com", "(404) 555-0192"),
            "provider": "Patty Postanowicz, Ph.D, LMFT",
            "location": "Marietta, GA",
            "description": "Client reports low mood, depression, grief, sleep difficulty, and loss of interest.",
        },
        {
            "label": "Couples therapy -> relational intake",
            "patient": ("Maya", "Patel", 1988, 3, 9, "Female", "maya.patel@example.com", "(770) 555-0134"),
            "provider": "Jamie Goldberg, LPC, E-RYT",
            "location": "Alpharetta, GA",
            "description": "Couple seeking relationship support, communication work, and marital counseling.",
        },
        {
            "label": "Coaching goal -> coaching consent",
            "patient": ("Noah", "Chen", 1984, 11, 22, "Male", "noah.chen@example.com", "(678) 555-0150"),
            "provider": "Alan Behrman, Ph.D",
            "location": "Marietta, GA",
            "description": "Client requests executive coaching, leadership support, career decisions, and life goal planning.",
        },
        {
            "label": "Care coordination -> release authorization",
            "patient": ("Leila", "Nasser", 1985, 9, 25, "Female", "leila.nasser@example.com", "(504) 555-0180"),
            "provider": "David Dolese, LPC",
            "location": "New Orleans, LA",
            "description": "Client wants records coordinated with a physician and school counselor.",
        },
        {
            "label": "Anxiety and depression -> GAD-7 + PHQ-9",
            "patient": ("Arjun", "Sharma", 1998, 2, 14, "Male", "arjun.sharma@example.com", "(470) 555-0177"),
            "provider": "Dr. Ramakanth Vemuluri, MD",
            "location": "Duluth, GA",
            "description": "Client reports constant worry, panic attacks, depression, hopelessness, and trouble concentrating.",
        },
    ]

    output = []
    for scenario in scenarios:
        p = make_patient(db, *scenario["patient"])
        a = make_appointment(
            db,
            p.id,
            len(output) + 2,
            scenario["provider"],
            scenario["location"],
            scenario["description"],
        )
        total, done, form_ids = count_forms(db, a.id)
        output.append({
            "label": scenario["label"],
            "name": p.full_name,
            "forms": f"{done}/{total}",
            "token": a.intake_link_token,
            "form_ids": ", ".join(form_ids),
        })

    db.close()

    for scenario in output:
        print(f"\n{scenario['label']}")
        print(f"Client: {scenario['name']} | Forms: {scenario['forms']}")
        print(f"Assigned: {scenario['form_ids']}")
        print(f"{BASE_URL}/?t={scenario['token']}")

    print("\n" + "-" * 68)
    print(f"{len(output)} AlanBehrman intake links generated.")
    print("-" * 68 + "\n")


if __name__ == "__main__":
    run()
