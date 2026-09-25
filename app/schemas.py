from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, PositiveInt, field_validator


class InputModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class ProfileCreate(InputModel):
    name: Annotated[str, Field(min_length=1, max_length=120)]
    bio: Annotated[str | None, Field(max_length=2000)] = None
    avatar_url: HttpUrl | None = None
    github_url: HttpUrl | None = None
    linkedin_url: HttpUrl | None = None


class ProjectSummaryOut(ORMModel):
    id: int
    title: str


class ProfileOut(ORMModel):
    id: int
    name: str
    bio: str | None
    avatar_url: HttpUrl | None
    github_url: HttpUrl | None
    linkedin_url: HttpUrl | None
    created_at: datetime
    projects: list[ProjectSummaryOut] = Field(default_factory=list)


class TechnologyCreate(InputModel):
    name: Annotated[str, Field(min_length=1, max_length=80)]
    description: Annotated[str | None, Field(max_length=300)] = None


class TechnologyOut(ORMModel):
    id: int
    name: str
    description: str | None


class FeedbackCreate(InputModel):
    author_name: Annotated[str, Field(min_length=1, max_length=120)]
    comment: Annotated[str, Field(min_length=1, max_length=2000)]
    rating: Annotated[int, Field(ge=1, le=5)]
    project_id: PositiveInt


class FeedbackOut(ORMModel):
    id: int
    author_name: str
    comment: str
    rating: int
    project_id: int
    created_at: datetime


class ProjectCreate(InputModel):
    title: Annotated[str, Field(min_length=1, max_length=160)]
    description: Annotated[str | None, Field(max_length=4000)] = None
    repository_url: HttpUrl | None = None
    demo_url: HttpUrl | None = None
    profile_id: PositiveInt
    technology_ids: list[PositiveInt] = Field(default_factory=list)

    @field_validator("technology_ids")
    @classmethod
    def technology_ids_must_be_unique(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("Não repita tecnologias no mesmo projeto.")
        return value


class ProjectOut(ORMModel):
    id: int
    title: str
    description: str | None
    repository_url: HttpUrl | None
    demo_url: HttpUrl | None
    profile_id: int
    technologies: list[TechnologyOut] = Field(default_factory=list)
    feedbacks: list[FeedbackOut] = Field(default_factory=list)
