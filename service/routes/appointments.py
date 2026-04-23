from __future__ import annotations
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from service.database import get_db
from service import crud, schemas, models, notifications

router = APIRouter()


@router.post("/appointments", response_model=schemas.AppointmentOut, status_code=201)
def create_appointment(data: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    return crud.create_appointment(db, data)


@router.get("/appointments/upcoming", response_model=List[schemas.AppointmentSummary])
def list_upcoming_appointments(db: Session = Depends(get_db)):
    return crud.list_upcoming_appointments(db)


@router.get("/appointments/{appointment_id}", response_model=schemas.AppointmentOut)
def get_appointment(appointment_id: uuid.UUID, db: Session = Depends(get_db)):
    a = crud.get_appointment(db, appointment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return a


@router.get("/appointments/{appointment_id}/forms", response_model=List[schemas.FormStatus])
def get_appointment_forms(appointment_id: uuid.UUID, db: Session = Depends(get_db)):
    rows = crud.get_forms_for_appointment(db, appointment_id)
    return [
        schemas.FormStatus(
            id=pf.id,
            form_id=fd.id,
            title=fd.title,
            description=fd.description,
            category=fd.category,
            status=pf.status,
            is_required=fd.is_required,
            estimated_minutes=fd.estimated_minutes,
            sort_order=fd.sort_order,
            file_template=fd.file_template,
        )
        for pf, fd in rows
    ]


@router.post("/appointments/{appointment_id}/remind", response_model=schemas.ReminderResult)
def send_reminder(appointment_id: uuid.UUID, db: Session = Depends(get_db)):
    appt = crud.get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    patient = crud.get_patient(db, appt.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    form_rows = db.execute(
        select(models.PatientForm).where(models.PatientForm.appointment_id == appointment_id)
    ).scalars().all()

    forms_total     = len(form_rows)
    forms_completed = sum(1 for f in form_rows if f.status == "completed")

    if forms_total > 0 and forms_completed == forms_total:
        return schemas.ReminderResult(
            email_sent=False, sms_sent=False, remaining=0,
            message="All forms already completed — no reminder needed.",
        )

    result = notifications.send_reminder(
        patient_name=patient.full_name,
        patient_email=patient.email,
        patient_phone=patient.phone,
        appt_type_raw=appt.appointment_type,
        appt_date=appt.appointment_date,
        forms_done=forms_completed,
        forms_total=forms_total,
        intake_token=appt.intake_link_token,
    )
    return schemas.ReminderResult(**result)


@router.get("/intake/{token}", response_model=schemas.IntakeContext)
def get_intake_context(token: str, db: Session = Depends(get_db)):
    appt = crud.get_appointment_by_token(db, token)
    if not appt:
        raise HTTPException(status_code=404, detail="Invalid or expired intake link")

    patient = crud.get_patient(db, appt.patient_id)
    rows = crud.get_forms_for_appointment(db, appt.id)

    forms = [
        schemas.FormStatus(
            id=pf.id,
            form_id=fd.id,
            title=fd.title,
            description=fd.description,
            category=fd.category,
            status=pf.status,
            is_required=fd.is_required,
            estimated_minutes=fd.estimated_minutes,
            sort_order=fd.sort_order,
            file_template=fd.file_template,
        )
        for pf, fd in rows
    ]

    return schemas.IntakeContext(
        patient=schemas.PatientOut.model_validate(patient),
        appointment=schemas.AppointmentOut.model_validate(appt),
        forms=forms,
    )
