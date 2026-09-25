from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .database import create_schema, get_db
from .models import Profile, Project, Technology
from .schemas import ProfileCreate, ProfileOut, ProjectCreate, ProjectOut, TechnologyCreate, TechnologyOut


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    create_schema()
    yield


app = FastAPI(
    title="DevShowcase API",
    description="API para perfis de desenvolvedores, projetos, tecnologias e opiniões.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "DevShowcase API"}


@app.post("/api/profiles", response_model=ProfileOut, status_code=status.HTTP_201_CREATED, tags=["Profiles"])
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)) -> Profile:
    profile = Profile(
        name=payload.name,
        bio=payload.bio,
        avatar_url=str(payload.avatar_url) if payload.avatar_url else None,
        github_url=str(payload.github_url) if payload.github_url else None,
        linkedin_url=str(payload.linkedin_url) if payload.linkedin_url else None,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@app.get("/api/profiles/{profile_id}", response_model=ProfileOut, tags=["Profiles"])
def get_profile(profile_id: int, db: Session = Depends(get_db)) -> Profile:
    statement = select(Profile).options(selectinload(Profile.projects)).where(Profile.id == profile_id)
    profile = db.scalar(statement)
    if profile is None:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")
    return profile


@app.post("/api/technologies", response_model=TechnologyOut, status_code=status.HTTP_201_CREATED, tags=["Technologies"])
def create_technology(payload: TechnologyCreate, db: Session = Depends(get_db)) -> Technology:
    technology = Technology(name=payload.name, description=payload.description)
    db.add(technology)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe uma tecnologia com esse nome.") from exc
    db.refresh(technology)
    return technology


@app.get("/api/technologies", response_model=list[TechnologyOut], tags=["Technologies"])
def list_technologies(db: Session = Depends(get_db)) -> list[Technology]:
    return list(db.scalars(select(Technology).order_by(Technology.name)).all())


@app.post("/api/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED, tags=["Projects"])
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    profile = db.get(Profile, payload.profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Perfil informado não encontrado.")

    technologies: list[Technology] = []
    if payload.technology_ids:
        technologies = list(
            db.scalars(select(Technology).where(Technology.id.in_(payload.technology_ids))).all()
        )
        missing_ids = sorted(set(payload.technology_ids) - {item.id for item in technologies})
        if missing_ids:
            raise HTTPException(status_code=404, detail=f"Tecnologias não encontradas: {missing_ids}.")

    project = Project(
        title=payload.title,
        description=payload.description,
        repository_url=str(payload.repository_url) if payload.repository_url else None,
        demo_url=str(payload.demo_url) if payload.demo_url else None,
        profile=profile,
        technologies=technologies,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _load_project(db, project.id)


@app.get("/api/projects", response_model=list[ProjectOut], tags=["Projects"])
def list_projects(db: Session = Depends(get_db)) -> list[Project]:
    statement = (
        select(Project)
        .options(selectinload(Project.technologies), selectinload(Project.feedbacks))
        .order_by(Project.id)
    )
    return list(db.scalars(statement).all())


def _load_project(db: Session, project_id: int) -> Project:
    statement = (
        select(Project)
        .options(selectinload(Project.technologies), selectinload(Project.feedbacks))
        .where(Project.id == project_id)
    )
    project = db.scalar(statement)
    if project is None:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    return project
