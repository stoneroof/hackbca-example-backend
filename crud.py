from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

import models
import schemas


def unpack_project(db: Session, project: schemas.ProjectIn):
    user_ids = (u.id for u in project.users)
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    return {**project.dict(exclude_unset=True), "users": users}


def list_all_projects(db: Session):
    return db.query(models.Project).all()


def get_project(db: Session, uuid: UUID):
    return db.query(models.Project).filter_by(id = uuid).one_or_none()


def create_project(db: Session, project: schemas.ProjectIn):
    db_project = models.Project(**unpack_project(db, project))
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project(db: Session, uuid: UUID, project: schemas.ProjectIn):
    db_project = get_project(db, uuid)
    if db_project is None:
        return None

    project_data = unpack_project(db, project)
    for key, value in project_data.items():
        setattr(db_project, key, value)

    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, uuid: UUID):
    if db_project := get_project(db, uuid):
        db.delete(db_project)
        db.commit()
        return True

    return False
