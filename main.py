from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Literal, List, Optional
from uuid import UUID, uuid4

app = FastAPI()

class ProjectIn(BaseModel):
    name: str
    owner: List[str]
    date_proposed: datetime
    time: datetime
    type: Literal["software", "hardware"]
    description: Optional[str]
    github: Optional[str]
    url: Optional[str]


class Project(ProjectIn):
    id: UUID


projects: Dict[UUID, Project] = {}


def auth():
    # TODO: implement
    return True


@app.get("/projects", response_model=List[Project])
async def list_projects():
    return list(projects.values())


@app.get("/project/{uuid}", response_model=Project)
async def get_project(uuid: UUID):
    if uuid not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    return projects[uuid]


@app.post("/projects", response_model=Project)
async def create_project(project: ProjectIn):
    if not auth():
        raise HTTPException(status_code=404, detail="Not authenticated")

    uuid = uuid4()
    while uuid in projects:
        uuid = uuid4()

    project = Project(**project.dict(), id=uuid)
    projects[uuid] = project

    return project


@app.put("/projects/{uuid}", response_model=Project)
async def update_project(uuid: UUID, project: ProjectIn):
    if not auth():
        raise HTTPException(status_code=404, detail="Not authenticated")

    if uuid not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = Project(**project.dict(), id=uuid)
    projects[uuid] = project

    return project
