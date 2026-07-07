"""
Seeds AlanBehrman form definitions and creates one demo intake.

Run from elevia-AlanBehrman/:
    python service/seed.py
"""
import os
import sys
from datetime import datetime, timezone, date

from sqlalchemy import delete, select

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
        title="Billing Policy",
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


SYNTHETIC_PROVIDER_NAME = "Dr. Patty Postanowicz"
SYNTHETIC_PATIENTS = [
    {
        "full_name": "Maya Chen",
        "first_name": "Maya",
        "dob": date(1991, 3, 12),
        "gender": "Female",
        "email": "maya.chen@example.com",
        "phone": "(404) 555-0101",
        "appointment_type": "therapy_consultation",
        "appointment_date": datetime(2026, 7, 9, 10, 0, tzinfo=timezone.utc),
        "note": {
            "note_type": "Progress Note",
            "encounter_date": datetime(2026, 7, 9, 10, 30, tzinfo=timezone.utc),
            "service_location": "Telehealth",
            "place_of_service_code": "02",
            "chief_complaint": "Anxiety and difficulty sleeping following a recent work transition.",
            "subjective": "Client reports increased worry, restlessness, and frequent early-morning awakenings over the past three weeks. She reports feeling tense at work and struggling to concentrate.",
            "objective": "Affect appropriate, no psychomotor agitation. Speech normal. Mood anxious but stable. Sleep reported as fragmented. No acute safety concerns.",
            "assessment": "Generalized anxiety disorder with mild insomnia. Symptoms currently manageable but persistent.",
            "plan": "Continue CBT-based coping skills, limit caffeine, and reassess sleep hygiene in one week. Follow-up scheduled in 2 weeks.",
            "diagnosis_codes": [{"pointer": "A", "code": "F41.1", "description": "Generalized anxiety disorder"}],
            "procedure_codes": [{"code": "90837", "description": "Psychotherapy, 60 min", "units": 1, "modifiers": []}],
        },
    },
    {
        "full_name": "Jordan Alvarez",
        "first_name": "Jordan",
        "dob": date(1988, 8, 24),
        "gender": "Nonbinary",
        "email": "jordan.alvarez@example.com",
        "phone": "(404) 555-0102",
        "appointment_type": "therapy_consultation",
        "appointment_date": datetime(2026, 7, 10, 12, 30, tzinfo=timezone.utc),
        "note": {
            "note_type": "SOAP Note",
            "encounter_date": datetime(2026, 7, 10, 13, 0, tzinfo=timezone.utc),
            "service_location": "Private Practice Office",
            "place_of_service_code": "11",
            "chief_complaint": "Low motivation and persistent sadness after a breakup.",
            "subjective": "Client reports feeling emotionally flat, tearful, and less interested in hobbies. Motivation for exercise and socializing has declined over the past month.",
            "objective": "Mood down, affect constricted. No psychosis. Energy low but adequate. Engagement with treatment is good.",
            "assessment": "Major depressive disorder, recurrent episode, mild. Adjustment symptoms related to recent relational loss.",
            "plan": "Continue supportive psychotherapy; introduce behavioral activation goals. Monitor mood over next week. Medication review pending.",
            "diagnosis_codes": [{"pointer": "A", "code": "F32.9", "description": "Major depressive disorder, single episode, unspecified"}],
            "procedure_codes": [{"code": "90832", "description": "Psychotherapy, 30 min", "units": 1, "modifiers": []}],
        },
    },
    {
        "full_name": "Liam Brooks",
        "first_name": "Liam",
        "dob": date(1976, 11, 2),
        "gender": "Male",
        "email": "liam.brooks@example.com",
        "phone": "(404) 555-0103",
        "appointment_type": "therapy_consultation",
        "appointment_date": datetime(2026, 7, 12, 9, 30, tzinfo=timezone.utc),
        "note": {
            "note_type": "Progress Note",
            "encounter_date": datetime(2026, 7, 12, 10, 0, tzinfo=timezone.utc),
            "service_location": "Telehealth",
            "place_of_service_code": "02",
            "chief_complaint": "Stress management and anger management support.",
            "subjective": "Client reports irritability and tension at home, especially around parenting stress. He notes avoiding difficult conversations.",
            "objective": "Alert and oriented. Affect mildly tense. No safety concerns. Reports making progress with grounding techniques.",
            "assessment": "Stress-related symptoms with intermittent anger dysregulation. No current evidence of aggression.",
            "plan": "Continue weekly sessions. Practice pause-and-breathe strategies between appointments. Reassess coping responses next visit.",
            "diagnosis_codes": [{"pointer": "A", "code": "F43.8", "description": "Other specified reactions to severe stress"}],
            "procedure_codes": [{"code": "90837", "description": "Psychotherapy, 60 min", "units": 1, "modifiers": []}],
        },
    },
    {
        "full_name": "Sofia Ramirez",
        "first_name": "Sofia",
        "dob": date(1994, 5, 18),
        "gender": "Female",
        "email": "sofia.ramirez@example.com",
        "phone": "(404) 555-0104",
        "appointment_type": "therapy_consultation",
        "appointment_date": datetime(2026, 7, 13, 13, 0, tzinfo=timezone.utc),
        "note": {
            "note_type": "Progress Note",
            "encounter_date": datetime(2026, 7, 13, 13, 30, tzinfo=timezone.utc),
            "service_location": "Private Practice Office",
            "place_of_service_code": "11",
            "chief_complaint": "Persistent worry around social situations and performance at work.",
            "subjective": "Client reports racing thoughts before presentations and difficulty relaxing after meetings. She feels physically tense and avoids saying no to extra tasks.",
            "objective": "No acute distress. Breathing regular. Warm affect. Demonstrates insight and motivation.",
            "assessment": "Social anxiety with generalized worry. Functioning mostly preserved.",
            "plan": "Continue exposure-based work and cognitive restructuring. Practice short exposure exercises at least 3 times weekly.",
            "diagnosis_codes": [{"pointer": "A", "code": "F40.10", "description": "Social phobia, unspecified"}],
            "procedure_codes": [{"code": "90837", "description": "Psychotherapy, 60 min", "units": 1, "modifiers": []}],
        },
    },
    {
        "full_name": "Noah Patel",
        "first_name": "Noah",
        "dob": date(1983, 1, 30),
        "gender": "Male",
        "email": "noah.patel@example.com",
        "phone": "(404) 555-0105",
        "appointment_type": "therapy_consultation",
        "appointment_date": datetime(2026, 7, 14, 11, 0, tzinfo=timezone.utc),
        "note": {
            "note_type": "SOAP Note",
            "encounter_date": datetime(2026, 7, 14, 11, 30, tzinfo=timezone.utc),
            "service_location": "Telehealth",
            "place_of_service_code": "02",
            "chief_complaint": "Difficulty managing grief after the loss of a parent.",
            "subjective": "Client reports waves of sadness, guilt, and interrupted sleep. He wants help processing the loss and returning to routine.",
            "objective": "Mood sad but stable. No hopelessness or SI. Insight improving with each session.",
            "assessment": "Persistent complex bereavement symptoms with adjustment difficulties.",
            "plan": "Continue grief-focused therapy and support pacing of daily routine. Encourage journaling and grief support group.",
            "diagnosis_codes": [{"pointer": "A", "code": "F43.21", "description": "Separation anxiety disorder"}],
            "procedure_codes": [{"code": "90832", "description": "Psychotherapy, 30 min", "units": 1, "modifiers": []}],
        },
    },
    {
        "full_name": "Ava Thompson",
        "first_name": "Ava",
        "dob": date(1997, 9, 8),
        "gender": "Female",
        "email": "ava.thompson@example.com",
        "phone": "(404) 555-0106",
        "appointment_type": "therapy_consultation",
        "appointment_date": datetime(2026, 7, 15, 15, 30, tzinfo=timezone.utc),
        "note": {
            "note_type": "Progress Note",
            "encounter_date": datetime(2026, 7, 15, 16, 0, tzinfo=timezone.utc),
            "service_location": "Private Practice Office",
            "place_of_service_code": "11",
            "chief_complaint": "Burnout and emotional exhaustion from work demands.",
            "subjective": "Client reports feeling drained, irritable, and unable to fully disconnect from work after hours. She wants help setting boundaries.",
            "objective": "Affect mildly fatigued. Reports good engagement and insight. No acute safety concerns.",
            "assessment": "Occupational stress with early burnout symptoms. No current depression or anxiety diagnosis.",
            "plan": "Work on boundary-setting, time management, and self-compassion. Reassess stress load in two weeks.",
            "diagnosis_codes": [{"pointer": "A", "code": "Z73.3", "description": "Stress, not elsewhere classified"}],
            "procedure_codes": [{"code": "90837", "description": "Psychotherapy, 60 min", "units": 1, "modifiers": []}],
        },
    },
    {
        "full_name": "Ethan Rivera",
        "first_name": "Ethan",
        "dob": date(1989, 6, 16),
        "gender": "Male",
        "email": "ethan.rivera@example.com",
        "phone": "(404) 555-0107",
        "appointment_type": "therapy_consultation",
        "appointment_date": datetime(2026, 7, 16, 10, 30, tzinfo=timezone.utc),
        "note": {
            "note_type": "Progress Note",
            "encounter_date": datetime(2026, 7, 16, 11, 0, tzinfo=timezone.utc),
            "service_location": "Telehealth",
            "place_of_service_code": "02",
            "chief_complaint": "Relationship stress and repeated conflict with partner.",
            "subjective": "Client reports recurring arguments and difficulty repairing after conflict. He wants support with communication and emotional regulation.",
            "objective": "Affect calm. Demonstrates motivation to learn communication tools. No acute distress.",
            "assessment": "Relationship distress with moderate interpersonal conflict. No current mood episode.",
            "plan": "Introduce communication exercises and weekly practice. Continue structured sessions for two more visits.",
            "diagnosis_codes": [{"pointer": "A", "code": "Z63.0", "description": "Problems in relationship with spouse or partner"}],
            "procedure_codes": [{"code": "90837", "description": "Psychotherapy, 60 min", "units": 1, "modifiers": []}],
        },
    },
    {
        "full_name": "Isabella Cruz",
        "first_name": "Isabella",
        "dob": date(1992, 2, 7),
        "gender": "Female",
        "email": "isabella.cruz@example.com",
        "phone": "(404) 555-0108",
        "appointment_type": "therapy_consultation",
        "appointment_date": datetime(2026, 7, 18, 14, 0, tzinfo=timezone.utc),
        "note": {
            "note_type": "SOAP Note",
            "encounter_date": datetime(2026, 7, 18, 14, 30, tzinfo=timezone.utc),
            "service_location": "Private Practice Office",
            "place_of_service_code": "11",
            "chief_complaint": "Overthinking and perfectionism affecting daily functioning.",
            "subjective": "Client reports intrusive self-criticism and delayed task completion due to perfectionistic standards. She feels tired and frustrated by this cycle.",
            "objective": "Affect anxious but engaged. Insight intact. No safety concerns. Good participation in session.",
            "assessment": "Perfectionism with anxious cognitions and mild depressive symptoms.",
            "plan": "Introduce cognitive defusion and goal-setting exercises. Continue weekly sessions and monitor mood.",
            "diagnosis_codes": [{"pointer": "A", "code": "F41.8", "description": "Other specified anxiety disorders"}],
            "procedure_codes": [{"code": "90832", "description": "Psychotherapy, 30 min", "units": 1, "modifiers": []}],
        },
    },
    {
        "full_name": "Marcus Bell",
        "first_name": "Marcus",
        "dob": date(1985, 12, 1),
        "gender": "Male",
        "email": "marcus.bell@example.com",
        "phone": "(404) 555-0109",
        "appointment_type": "therapy_consultation",
        "appointment_date": datetime(2026, 7, 20, 16, 0, tzinfo=timezone.utc),
        "note": {
            "note_type": "Progress Note",
            "encounter_date": datetime(2026, 7, 20, 16, 30, tzinfo=timezone.utc),
            "service_location": "Telehealth",
            "place_of_service_code": "02",
            "chief_complaint": "Support with self-esteem and identity-related stress.",
            "subjective": "Client reports feeling stuck in a transition period and struggling with confidence. He wants help reframing self-critical thoughts.",
            "objective": "Mood steady. Speech clear. Cooperative and engaged. Good insight into patterns of self-judgment.",
            "assessment": "Low self-esteem with situational stress. No acute psychiatric symptoms.",
            "plan": "Continue strength-based therapy, complete self-esteem journaling exercises, and revisit goals next week.",
            "diagnosis_codes": [{"pointer": "A", "code": "R45.81", "description": "Low self-esteem"}],
            "procedure_codes": [{"code": "90837", "description": "Psychotherapy, 60 min", "units": 1, "modifiers": []}],
        },
    },
    {
        "full_name": "Grace Nguyen",
        "first_name": "Grace",
        "dob": date(1990, 7, 27),
        "gender": "Female",
        "email": "grace.nguyen@example.com",
        "phone": "(404) 555-0110",
        "appointment_type": "therapy_consultation",
        "appointment_date": datetime(2026, 7, 22, 8, 30, tzinfo=timezone.utc),
        "note": {
            "note_type": "Progress Note",
            "encounter_date": datetime(2026, 7, 22, 9, 0, tzinfo=timezone.utc),
            "service_location": "Private Practice Office",
            "place_of_service_code": "11",
            "chief_complaint": "Support with panic symptoms and avoidance behaviors.",
            "subjective": "Client reports episodes of chest tightness, racing heart, and fear of losing control in crowded settings. She has started avoiding errands and social events.",
            "objective": "Anxious but cooperative. No acute panic episode during session. Respirations even. Good insight into avoidance cycle.",
            "assessment": "Panic disorder with agoraphobic avoidance tendencies.",
            "plan": "Continue exposure hierarchy and breathing retraining. Practice one exposure step daily before next visit.",
            "diagnosis_codes": [{"pointer": "A", "code": "F41.0", "description": "Panic disorder"}],
            "procedure_codes": [{"code": "90837", "description": "Psychotherapy, 60 min", "units": 1, "modifiers": []}],
        },
    },
]


def seed_synthetic_patients(db):
    created = 0
    for index, payload in enumerate(SYNTHETIC_PATIENTS, start=1):
        existing_patient = db.execute(
            select(models.Patient).where(models.Patient.email == payload["email"])
        ).scalar_one_or_none()
        if existing_patient:
            patient = existing_patient
        else:
            patient = crud.create_patient(db, schemas.PatientCreate(
                full_name=payload["full_name"],
                first_name=payload["first_name"],
                dob=payload["dob"],
                gender=payload["gender"],
                email=payload["email"],
                phone=payload["phone"],
            ))

        existing_appt = db.execute(
            select(models.Appointment).where(
                models.Appointment.patient_id == patient.id,
                models.Appointment.appointment_date == payload["appointment_date"],
                models.Appointment.provider_name == SYNTHETIC_PROVIDER_NAME,
            )
        ).scalar_one_or_none()
        if existing_appt:
            appt = existing_appt
        else:
            appt = crud.create_appointment(db, schemas.AppointmentCreate(
                patient_id=patient.id,
                appointment_type=payload["appointment_type"],
                appointment_date=payload["appointment_date"],
                provider_name=SYNTHETIC_PROVIDER_NAME,
                clinic_location="Atlanta, GA",
                appointment_description=f"Synthetic TherapyNotes demo visit for {payload['full_name']}.",
            ))

        existing_note = db.execute(
            select(models.ClinicalNote).where(models.ClinicalNote.patient_id == patient.id, models.ClinicalNote.appointment_id == appt.id)
        ).scalar_one_or_none()
        if existing_note:
            continue

        note_payload = payload["note"]
        db.add(models.ClinicalNote(
            patient_id=patient.id,
            appointment_id=appt.id,
            tebra_encounter_id=f"ENC-{100400 + index}",
            tebra_chart_number=f"CH-{200800 + index}",
            tebra_case_id=f"CASE-{3000 + index}",
            note_type=note_payload["note_type"],
            encounter_date=note_payload["encounter_date"],
            service_location=note_payload["service_location"],
            place_of_service_code=note_payload["place_of_service_code"],
            rendering_provider_name=SYNTHETIC_PROVIDER_NAME,
            rendering_provider_npi="1987654321",
            chief_complaint=note_payload["chief_complaint"],
            subjective=note_payload["subjective"],
            objective=note_payload["objective"],
            assessment=note_payload["assessment"],
            plan=note_payload["plan"],
            diagnosis_codes=note_payload["diagnosis_codes"],
            procedure_codes=note_payload["procedure_codes"],
            encounter_status="Rendered",
            signed_by=SYNTHETIC_PROVIDER_NAME,
            signed_at=note_payload["encounter_date"],
        ))
        created += 1

    db.commit()
    print(f"Seeded {created} synthetic TherapyNotes-style clinical notes for {len(SYNTHETIC_PATIENTS)} patients assigned to {SYNTHETIC_PROVIDER_NAME}")


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

    seed_synthetic_patients(db)

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
