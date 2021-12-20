from fastapi import Depends, FastAPI, HTTPException, Cookie
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.sessions import SessionMiddleware
from typing import List, Optional
from uuid import UUID

from auth import oauth
from database import engine, SessionLocal
from models import Base
from schemas import Project, ProjectIn, User, UserInternal, UserOut
from settings import SESSION_SECRET
import crud

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins="*", allow_credentials="*", allow_methods=["*"], allow_headers=["*"])
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def authenticate(db: Session = Depends(get_db), hackbca_token: Optional[UUID] = Cookie(None)):
    if hackbca_token is not None:
        user = crud.get_user_by_token(db, hackbca_token)
        return user
    return None


response_401 = {401: {"description": "Not authenticated"}}
response_403 = {403: {"description": "Forbidden"}}
response_404 = {404: {"description": "Project not found"}}


# Handle Google token redirect
@app.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for("auth_via_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/google")
async def auth_via_google(request: Request, response: Response, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    id_token = await oauth.google.parse_id_token(request, token)
    sub = id_token["sub"]
    user = crud.get_user_by_subject(db, sub)
    if user is None:
        user = UserInternal(google_subject=sub, email=id_token["email"])
        user = crud.create_user(db, user)
    hackbca_token = crud.create_token(db, user.id)
    response.set_cookie(key="hackbca_token", value=hackbca_token, expires=None)
    return {"message": "Successfully logged in", "id": user.id} 


@app.get("/me", response_model=dict, responses=response_401)
async def me(user: Optional[UserOut] = Depends(authenticate)):
    if user is not None:
        return {"id": user.id, "email": user.email}
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")

@app.get("/logout")
async def logout(response: Response):
    response.set_cookie(key="hackbca_token", value="", expires=0)
    return {"message": "Successfully logged out"}


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
        raise HTTPException(status_code=403, detail="Forbidden")

    return crud.create_project(db, project)


@app.put("/projects/{uuid}", response_model=Project, responses=response_403|response_404)
async def update_project(uuid: UUID, project: ProjectIn, db: Session = Depends(get_db)):
    if not auth():
        raise HTTPException(status_code=403, detail="Forbidden")

    if res := crud.update_project(db, uuid, project):
        return res
    else:
        raise HTTPException(status_code=404, detail="Project not found")


@app.delete("/projects/{uuid}", responses=response_403|response_404)
async def update_project(uuid: UUID, db: Session = Depends(get_db)):
    if not auth():
        raise HTTPException(status_code=403, detail="Forbidden")

    if crud.delete_project(db, uuid):
        return
    else:
        raise HTTPException(status_code=404, detail="Project not found")


@app.get("/users", response_model=List[UserOut])
async def list_users(db: Session = Depends(get_db)):
    return crud.list_all_users(db)
