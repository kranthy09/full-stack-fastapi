from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Resume,
    ResumeCreate,
    ResumePublic,
    ResumesPublic,
    ResumeUpdate,
    Message,
)

router = APIRouter()


@router.get("/", response_model=ResumesPublic)
def read_resumes(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve resumes.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Resume)
        count = session.exec(count_statement).one()
        statement = select(Resume).offset(skip).limit(limit)
        resumes = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Resume)
            .where(Resume.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Resume)
            .where(Resume.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        resumes = session.exec(statement).all()

    return ResumesPublic(data=resumes, count=count)


@router.get("/{id}", response_model=ResumePublic)
def read_resume(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get resume by ID.
    """
    resume = session.get(Resume, id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not current_user.is_superuser and (resume.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return resume


@router.post("/", response_model=ResumePublic)
def create_resume(
    *, session: SessionDep, current_user: CurrentUser, resume_in: ResumeCreate
) -> Any:
    """
    Create new resume.
    """
    resume = Resume.model_validate(resume_in, update={"owner_id": current_user.id})
    session.add(resume)
    session.commit()
    session.refresh(resume)
    return resume


@router.put("/{id}", response_model=ResumePublic)
def update_resume(
    *, session: SessionDep, current_user: CurrentUser, id: int, resume_in: ResumeUpdate
) -> Any:
    """
    Update an resume.
    """
    resume = session.get(Resume, id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not current_user.is_superuser and (resume.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = resume_in.model_dump(exclude_unset=True)
    resume.sqlmodel_update(update_dict)
    session.add(resume)
    session.commit()
    session.refresh(resume)
    return resume


@router.delete("/{id}")
def delete_resume(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a resume.
    """
    resume = session.get(Resume, id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not current_user.is_superuser and (resume.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(resume)
    session.commit()
    return Message(message="Resume deleted successfully")
