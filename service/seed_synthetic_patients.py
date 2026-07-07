"""
Seeds 10 synthetic (fake) patients into the Patient Registry, each assigned to
one of two providers, with treatment/progress notes that mimic the fields
captured by the Tebra EMR (encounter id, chart number, case id, service
location, place-of-service code, rendering provider + NPI, SOAP note body,
ICD-10 diagnosis pointers, and CPT procedure codes).

Run from elevia-AlanBehrman/:
    python service/seed_synthetic_patients.py
"""
import os
import sys
import random
from datetime import datetime, timezone, timedelta, date

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from service.database import engine, SessionLocal
from service import models, crud, schemas

random.seed(42)

PROVIDERS = [
    {"name": "Dr. Ramakanth Vemuluri, MD", "npi": "1720384950", "specialty": "Psychiatry & Primary Care"},
    {"name": "Meredith Mitchell, PMHNP-BC", "npi": "1932847561", "specialty": "Psychiatric Mental Health"},
]

CLINIC_LOCATIONS = ["Marietta, GA", "Alpharetta, GA — Telehealth"]

PATIENTS = [
    {"full_name": "Maria Gonzalez",      "first_name": "Maria",     "dob": date(1988, 2, 11), "gender": "Female", "email": "maria.gonzalez@example.com",  "phone": "(404) 555-0102"},
    {"full_name": "James Whitfield",     "first_name": "James",     "dob": date(1975, 9, 23), "gender": "Male",   "email": "james.whitfield@example.com", "phone": "(404) 555-0113"},
    {"full_name": "Aisha Thompson",      "first_name": "Aisha",     "dob": date(1993, 6, 5),  "gender": "Female", "email": "aisha.thompson@example.com",  "phone": "(404) 555-0124"},
    {"full_name": "Daniel Kim",          "first_name": "Daniel",    "dob": date(1982, 12, 30),"gender": "Male",   "email": "daniel.kim@example.com",      "phone": "(404) 555-0135"},
    {"full_name": "Olivia Bennett",      "first_name": "Olivia",    "dob": date(1997, 4, 17), "gender": "Female", "email": "olivia.bennett@example.com",  "phone": "(404) 555-0146"},
    {"full_name": "Marcus Reed",         "first_name": "Marcus",    "dob": date(1969, 8, 2),  "gender": "Male",   "email": "marcus.reed@example.com",     "phone": "(404) 555-0157"},
    {"full_name": "Priya Natarajan",     "first_name": "Priya",     "dob": date(1991, 1, 28), "gender": "Female", "email": "priya.natarajan@example.com", "phone": "(404) 555-0168"},
    {"full_name": "Ethan Caldwell",      "first_name": "Ethan",     "dob": date(1985, 10, 9), "gender": "Male",   "email": "ethan.caldwell@example.com",  "phone": "(404) 555-0179"},
    {"full_name": "Sofia Alvarez",       "first_name": "Sofia",     "dob": date(2000, 5, 14), "gender": "Female", "email": "sofia.alvarez@example.com",   "phone": "(404) 555-0180"},
    {"full_name": "Nathaniel Brooks",    "first_name": "Nathaniel", "dob": date(1978, 3, 21), "gender": "Male",   "email": "nathaniel.brooks@example.com","phone": "(404) 555-0191"},
]

# Presenting concern per patient drives the description-keyword screener in
# crud.create_appointment (phq9 / gad7 / relational / coaching flags).
CONCERNS = [
    "New client intake for generalized anxiety, panic attacks, and difficulty sleeping.",
    "Follow-up medication management for major depressive disorder; reports improved mood.",
    "New client intake for work-related stress and anxiety, requests coping strategies.",
    "Follow-up for ADHD medication management; reviewing stimulant titration.",
    "New client intake for low mood, grief following recent loss, and social withdrawal.",
    "Follow-up for chronic insomnia and generalized anxiety disorder.",
    "New client intake for panic disorder with associated health anxiety.",
    "Follow-up medication check for bipolar II disorder, mood stable on current regimen.",
    "New client intake for adjustment disorder related to relationship transition.",
    "Follow-up for major depressive disorder; assessing response to SSRI dose increase.",
]

# (diagnosis codes, procedure code, SOAP snippets) keyed by note archetype
NOTE_ARCHETYPES = [
    {
        "dx": [{"pointer": "A", "code": "F41.1", "description": "Generalized anxiety disorder"}],
        "cpt": [{"code": "90837", "description": "Psychotherapy, 60 minutes", "units": 1, "modifiers": []}],
        "cc": "Anxiety, difficulty sleeping",
        "subjective": "Client reports persistent worry, racing thoughts at night, and difficulty falling asleep. Denies suicidal ideation. Endorses mild improvement in daytime anxiety since last session.",
        "objective": "Alert and oriented x4. Speech normal rate/rhythm. Affect mildly anxious, mood \"okay.\" No psychomotor agitation observed.",
        "assessment": "Generalized anxiety disorder, improving with current treatment plan.",
        "plan": "Continue weekly psychotherapy. Introduced progressive muscle relaxation technique. Reassess sleep hygiene at next visit.",
        "note_type": "SOAP Note",
    },
    {
        "dx": [{"pointer": "A", "code": "F33.1", "description": "Major depressive disorder, recurrent, moderate"}],
        "cpt": [{"code": "99214", "description": "Established patient E/M, moderate complexity", "units": 1, "modifiers": ["25"]}],
        "cc": "Depression, medication follow-up",
        "subjective": "Client reports improved energy and mood since sertraline increase 4 weeks ago. Sleep and appetite normalized. No side effects reported.",
        "objective": "PHQ-9 score decreased from 16 to 9 since last visit. Affect brighter, congruent with reported mood.",
        "assessment": "Major depressive disorder, recurrent, moderate — responding well to current SSRI dose.",
        "plan": "Continue sertraline 100mg daily. Follow up in 6 weeks. Continue supportive psychotherapy.",
        "note_type": "Progress Note",
    },
    {
        "dx": [{"pointer": "A", "code": "F41.9", "description": "Anxiety disorder, unspecified"}, {"pointer": "B", "code": "Z56.9", "description": "Occupational problem, unspecified"}],
        "cpt": [{"code": "90834", "description": "Psychotherapy, 45 minutes", "units": 1, "modifiers": []}],
        "cc": "Work-related stress",
        "subjective": "Client describes ongoing workplace conflict contributing to elevated stress and irritability. Reports using breathing exercises with some benefit.",
        "objective": "Cooperative, engaged in session. Mood euthymic, affect full range.",
        "assessment": "Adjustment reaction with anxious features related to occupational stressor.",
        "plan": "Continue biweekly therapy. Introduced cognitive restructuring exercises for workplace triggers.",
        "note_type": "SOAP Note",
    },
    {
        "dx": [{"pointer": "A", "code": "F90.0", "description": "ADHD, predominantly inattentive type"}],
        "cpt": [{"code": "99213", "description": "Established patient E/M, low complexity", "units": 1, "modifiers": []}],
        "cc": "ADHD medication management",
        "subjective": "Client reports improved focus at work since dose adjustment. Mild appetite suppression noted, otherwise tolerating well.",
        "objective": "Vital signs stable. No tics or tremor observed. Affect attentive and engaged.",
        "assessment": "ADHD, inattentive type — good response to current stimulant titration.",
        "plan": "Continue current dose of extended-release methylphenidate. Recheck BP/weight at next visit. Follow up in 4 weeks.",
        "note_type": "Progress Note",
    },
    {
        "dx": [{"pointer": "A", "code": "F32.1", "description": "Major depressive disorder, single episode, moderate"}, {"pointer": "B", "code": "Z63.4", "description": "Disappearance and death of family member"}],
        "cpt": [{"code": "90837", "description": "Psychotherapy, 60 minutes", "units": 1, "modifiers": []}],
        "cc": "Grief, low mood, social withdrawal",
        "subjective": "Client reports ongoing grief following recent loss of a parent, with low motivation and reduced social contact. No suicidal ideation.",
        "objective": "Tearful at times during session, otherwise cooperative. Mood depressed, affect congruent.",
        "assessment": "Major depressive episode with prominent grief reaction.",
        "plan": "Continue weekly grief-focused psychotherapy. Encouraged gradual re-engagement with support network. Reassess for medication if no improvement in 4 weeks.",
        "note_type": "SOAP Note",
    },
]

DIAG_INDEX_BY_CONCERN = [0, 1, 2, 3, 4, 0, 2, 1, 4, 1]


def seed():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    created = []
    for i, pdata in enumerate(PATIENTS):
        existing = db.execute(
            models.Patient.__table__.select().where(models.Patient.email == pdata["email"])
        ).first()
        if existing:
            print(f"Skipping (already exists): {pdata['full_name']}")
            continue

        patient = crud.create_patient(db, schemas.PatientCreate(**pdata))

        provider = PROVIDERS[i % len(PROVIDERS)]
        clinic_location = CLINIC_LOCATIONS[i % len(CLINIC_LOCATIONS)]
        concern = CONCERNS[i]
        appt_date = datetime.now(timezone.utc) - timedelta(days=(i + 1) * 9)

        # Dr. Vemuluri sees patients for psychiatry consultations; Mitchell for therapy.
        appt_type = "psychiatry_consultation" if "Vemuluri" in provider["name"] else "therapy_consultation"

        appt = crud.create_appointment(db, schemas.AppointmentCreate(
            patient_id=patient.id,
            appointment_type=appt_type,
            appointment_date=appt_date,
            provider_name=provider["name"],
            clinic_location=clinic_location,
            appointment_description=concern,
        ))

        archetype = NOTE_ARCHETYPES[DIAG_INDEX_BY_CONCERN[i]]
        chart_number = f"CH-{100000 + i * 37}"
        case_id = f"CASE-{200000 + i * 53}"
        encounter_id = f"ENC-{300000 + i * 71}"

        note = models.ClinicalNote(
            patient_id=patient.id,
            appointment_id=appt.id,
            tebra_encounter_id=encounter_id,
            tebra_chart_number=chart_number,
            tebra_case_id=case_id,
            note_type=archetype["note_type"],
            encounter_date=appt_date,
            service_location="AlanBehrman Behavioral Health — " + clinic_location.split(" —")[0],
            place_of_service_code="02" if "Telehealth" in clinic_location else "11",
            rendering_provider_name=provider["name"],
            rendering_provider_npi=provider["npi"],
            chief_complaint=archetype["cc"],
            subjective=archetype["subjective"],
            objective=archetype["objective"],
            assessment=archetype["assessment"],
            plan=archetype["plan"],
            diagnosis_codes=archetype["dx"],
            procedure_codes=archetype["cpt"],
            encounter_status="Approved for Billing",
            signed_by=provider["name"],
            signed_at=appt_date + timedelta(hours=1),
        )
        db.add(note)
        db.commit()

        created.append((patient, provider, appt))
        print(f"Created patient: {patient.full_name}  →  provider: {provider['name']}  →  note: {archetype['note_type']} ({archetype['dx'][0]['code']})")

    print(f"\n{len(created)} synthetic patients created.")
    db.close()


if __name__ == "__main__":
    seed()
