from __future__ import annotations
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from service.database import get_db
from service import crud, schemas

router = APIRouter()


@router.patch("/forms/{patient_form_id}", response_model=dict)
def update_form_status(
    patient_form_id: uuid.UUID,
    data: schemas.PatientFormUpdate,
    db: Session = Depends(get_db),
):
    pf = crud.update_patient_form(db, patient_form_id, data)
    if not pf:
        raise HTTPException(status_code=404, detail="Patient form not found")
    return {
        "id": str(pf.id),
        "form_id": pf.form_id,
        "status": pf.status,
        "completed_at": pf.completed_at.isoformat() if pf.completed_at else None,
    }


@router.put("/forms/{patient_form_id}/fields", response_model=dict)
def upsert_fields(
    patient_form_id: uuid.UUID,
    data: schemas.FieldsUpsert,
    db: Session = Depends(get_db),
):
    ok = crud.upsert_field_values(db, patient_form_id, data.fields)
    if not ok:
        raise HTTPException(status_code=404, detail="Patient form not found")
    return {"ok": True, "saved": len(data.fields)}


@router.get("/forms/{patient_form_id}/fields", response_model=List[schemas.FieldValueOut])
def get_fields(patient_form_id: uuid.UUID, db: Session = Depends(get_db)):
    rows = crud.get_field_values(db, patient_form_id)
    return [
        schemas.FieldValueOut(
            field_id=r.field_id,
            field_value=r.field_value,
            collected_at=r.collected_at,
            collection_method=r.collection_method,
        )
        for r in rows
    ]
