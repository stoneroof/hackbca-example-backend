from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

import models
import schemas


def unpack_project(db: Session, project: schemas.ProjectIn, user: schemas.User = None):
    users = project.users
    if user:
        users.append(user.id)

    users = db.query(models.User).filter(models.User.id.in_(users)).all()
    return {**project.dict(exclude_unset=True), "users": users}


def list_all_projects(db: Session):
    return db.query(models.Project).all()


def get_project(db: Session, uuid: UUID):
    return db.query(models.Project).filter_by(id = uuid).one_or_none()


def create_project(db: Session, project: schemas.ProjectIn, user: schemas.User = None):
    db_project = models.Project(**unpack_project(db, project, user))
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


def list_all_users(db: Session):
    return db.query(models.User).all()


def create_user(db: Session, user: schemas.UserInternal):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_token(db: Session, token: UUID):
    token = db.query(models.LoginToken).filter_by(id = token).one_or_none()
    return token.user if token else None


def get_user_by_subject(db: Session, subject: str):
    return db.query(models.User).filter_by(google_subject = subject).one_or_none()


def create_token(db: Session, user_id: UUID):
    token = models.LoginToken(user_id = user_id)
    db.add(token)
    db.commit()
    db.refresh(token)
    return token.id
