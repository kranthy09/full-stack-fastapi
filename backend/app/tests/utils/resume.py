from sqlmodel import Session

from app import crud
from app.models import Resume, ResumeCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_resume(db: Session) -> Resume:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    resume_in = ResumeCreate(title=title, description=description)
    return crud.create_resume(session=db, resume_in=resume_in, owner_id=owner_id)
