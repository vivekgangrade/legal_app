from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from app.schemas import Case, CaseCreate, CaseUpdate
from app.models import cases_db, get_case_by_id
from app.utils.logger import logger

router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)

@router.post("/", response_model=Case, status_code=status.HTTP_201_CREATED)
async def create_case(case: CaseCreate):
    logger.info(f"Creating case: {case.title}")
    new_case = case.model_dump()
    new_case["id"] = len(cases_db) + 1
    new_case["created_at"] = datetime.now()
    new_case["updated_at"] = datetime.now()
    cases_db.append(new_case)
    return new_case

@router.get("/", response_model=List[Case])
async def read_cases():
    logger.info("Fetching all cases")
    return cases_db

@router.get("/{case_id}", response_model=Case)
async def read_case(case_id: int):
    case = get_case_by_id(case_id)
    if not case:
        logger.warning(f"Case not found: {case_id}")
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.put("/{case_id}", response_model=Case)
async def update_case(case_id: int, case_update: CaseUpdate):
    case = get_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    update_data = case_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        case[key] = value
    
    case["updated_at"] = datetime.now()
    return case

@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(case_id: int):
    case = get_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    cases_db.remove(case)
    return None
