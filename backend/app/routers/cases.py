from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlalchemy.orm import Session
from app.schemas import Case as CaseSchema, CaseCreate, CaseUpdate
from app.models import Case
from app.database import get_db
from app.utils.logger import logger

router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)

@router.post("/", response_model=CaseSchema, status_code=status.HTTP_201_CREATED)
async def create_case(case: CaseCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating case: {case.title}")
    new_case = Case(**case.model_dump())
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case

@router.get("/", response_model=List[CaseSchema])
async def read_cases(db: Session = Depends(get_db)):
    logger.info("Fetching all cases")
    cases = db.query(Case).all()
    return cases

@router.get("/{case_id}", response_model=CaseSchema)
async def read_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        logger.warning(f"Case not found: {case_id}")
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.put("/{case_id}", response_model=CaseSchema)
async def update_case(case_id: int, case_update: CaseUpdate, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    update_data = case_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(case, key, value)
    
    db.commit()
    db.refresh(case)
    return case

@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    db.delete(case)
    db.commit()
    return None
