from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.requests import Request
from typing import List
from uuid import UUID

from auth import oauth
from database import engine, SessionLocal
from models import Base
from schemas import Project, ProjectIn, User
import crud

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins="*", allow_credentials="*", allow_methods=["*"], allow_headers=["*"])

response_403 = {403: {"description": "Not authenticated"}}
response_404 = {404: {"description": "Project not found"}}

# Handle Google token redirect
@app.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for("auth_via_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google")
async def auth_via_google(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    return dict(user)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def auth():
    # TODO: implement
    return True


@app.get("/projects", response_model=List[Project])
async def list_projects(db: Session = Depends(get_db)):
    return crud.list_all_projects(db)


@app.get("/projects/{uuid}", response_model=Project, responses=response_404)
async def get_project(uuid: UUID, db: Session = Depends(get_db)):
    if res := crud.get_project(db, uuid):
        return res
    else:
        raise HTTPException(status_code=404, detail="Project not found")


@app.post("/projects", response_model=Project, responses=response_403)
async def create_project(project: ProjectIn, db: Session = Depends(get_db)):
    if not auth():
        raise HTTPException(status_code=403, detail="Not authenticated")

    return crud.create_project(db, project)


@app.put("/projects/{uuid}", response_model=Project, responses=response_403|response_404)
async def update_project(uuid: UUID, project: ProjectIn, db: Session = Depends(get_db)):
    if not auth():
        raise HTTPException(status_code=403, detail="Not authenticated")

    if res := crud.update_project(db, uuid, project):
        return res
    else:
        raise HTTPException(status_code=404, detail="Project not found")


@app.delete("/projects/{uuid}", responses=response_403|response_404)
async def update_project(uuid: UUID, db: Session = Depends(get_db)):
    if not auth():
        raise HTTPException(status_code=403, detail="Not authenticated")

    if crud.delete_project(db, uuid):
        return
    else:
        raise HTTPException(status_code=404, detail="Project not found")


@app.get("/users", response_model=List[User])
async def list_users(db: Session = Depends(get_db)):
    return crud.list_all_users(db)
