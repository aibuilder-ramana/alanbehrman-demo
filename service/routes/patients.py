import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from service.database import get_db
from service import crud, schemas

router = APIRouter()


@router.post("", response_model=schemas.PatientOut, status_code=201)
def create_patient(data: schemas.PatientCreate, db: Session = Depends(get_db)):
    return crud.create_patient(db, data)


@router.get("", response_model=List[schemas.PatientSummary])
def list_patients(
    q: Optional[str] = Query(None, description="Search by name, email, or phone"),
    db: Session = Depends(get_db),
):
    return crud.list_patients_with_stats(db, q)


@router.get("/{patient_id}", response_model=schemas.PatientOut)
def get_patient(patient_id: uuid.UUID, db: Session = Depends(get_db)):
    p = crud.get_patient(db, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p


@router.patch("/{patient_id}", response_model=schemas.PatientOut)
def update_patient(patient_id: uuid.UUID, data: schemas.PatientUpdate, db: Session = Depends(get_db)):
    p = crud.update_patient(db, patient_id, data)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p
