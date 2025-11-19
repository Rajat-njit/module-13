# app/routers/calculations.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database import get_db
from app.models.calculation import Calculation
from app.schemas.calculation import (
    CalculationBase,
    CalculationResponse,
    CalculationUpdate
)

router = APIRouter()



# --------- CREATE ---------
@router.post("", response_model=CalculationResponse, status_code=201)
def create_calculation(
    data: CalculationBase,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        calc = Calculation.create(
            calculation_type=data.type,
            user_id=user.id,
            inputs=data.inputs
        )
        calc.result = calc.get_result()

        db.add(calc)
        db.commit()
        db.refresh(calc)
        return calc
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --------- BROWSE ---------
@router.get("", response_model=list[CalculationResponse])
def list_calculations(
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(Calculation).filter(Calculation.user_id == user.id).all()


# --------- READ ---------
@router.get("/{calc_id}", response_model=CalculationResponse)
def get_calculation(
    calc_id: UUID,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    calc = db.query(Calculation).filter(
        Calculation.id == calc_id,
        Calculation.user_id == user.id
    ).first()

    if not calc:
        raise HTTPException(404, "Calculation not found")

    return calc


# --------- UPDATE ---------
@router.put("/{calc_id}", response_model=CalculationResponse)
def update_calculation(
    calc_id: UUID,
    data: CalculationUpdate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    calc = db.query(Calculation).filter(
        Calculation.id == calc_id,
        Calculation.user_id == user.id
    ).first()

    if not calc:
        raise HTTPException(404, "Calculation not found")

    if data.inputs is not None:
        calc.inputs = data.inputs
        calc.result = calc.get_result()

    db.commit()
    db.refresh(calc)
    return calc


# --------- DELETE ---------
@router.delete("/{calc_id}", status_code=204)
def delete_calculation(
    calc_id: UUID,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    calc = db.query(Calculation).filter(
        Calculation.id == calc_id,
        Calculation.user_id == user.id
    ).first()

    if not calc:
        raise HTTPException(404, "Calculation not found")

    db.delete(calc)
    db.commit()
    return None
