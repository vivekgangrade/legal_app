from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime, timezone
from app.schemas import CaseResponse, CaseCreate, CaseUpdate
from app.database import cases_collection, get_next_id
from app.utils.logger import logger

router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)


def case_doc_to_response(doc: dict) -> dict:
    """Convert MongoDB document to response format (strip _id)."""
    doc.pop("_id", None)
    return doc


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(case: CaseCreate):
    logger.info(f"Creating case: {case.title}")
    now = datetime.now(timezone.utc)
    case_doc = {
        "id": get_next_id("cases"),
        **case.model_dump(),
        "created_at": now,
        "updated_at": now,
    }
    cases_collection.insert_one(case_doc)
    return case_doc_to_response(case_doc)


@router.get("/", response_model=List[CaseResponse])
async def read_cases():
    logger.info("Fetching all cases")
    cases = list(cases_collection.find())
    return [case_doc_to_response(c) for c in cases]


@router.get("/{case_id}", response_model=CaseResponse)
async def read_case(case_id: int):
    case = cases_collection.find_one({"id": case_id})
    if not case:
        logger.warning(f"Case not found: {case_id}")
        raise HTTPException(status_code=404, detail="Case not found")
    return case_doc_to_response(case)


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(case_id: int, case_update: CaseUpdate):
    case = cases_collection.find_one({"id": case_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    update_data = case_update.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc)
        cases_collection.update_one({"id": case_id}, {"$set": update_data})

    updated_case = cases_collection.find_one({"id": case_id})
    return case_doc_to_response(updated_case)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(case_id: int):
    result = cases_collection.delete_one({"id": case_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Case not found")
    return None
