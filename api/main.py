"""REST galapunkti un Jinja lapas vienā FastAPI lietotnē."""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from game.names import validate_name
from pydantic import BaseModel, ConfigDict, Field, field_validator

from api.db import Database

API_DIR = Path(__file__).resolve().parent


class ScoreInput(BaseModel):
    """Spēlētāja vārds un nenegatīvs vesels punktu skaits."""

    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=24, strict=True)
    score: int = Field(ge=0, le=1_000_000_000, strict=True)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        """Pārbaudīt vārdu pēc tiem pašiem noteikumiem, kurus lieto spēle."""
        return validate_name(value)


class ScoreOutput(ScoreInput):
    """Saglabāts rezultāts ar identifikatoru un UTC laiku."""

    id: int
    created_at: str


class PlayerStats(BaseModel):
    """Visu spēļu kopsavilkums konkrētam spēlētāja vārdam."""

    name: str
    games: int
    best_score: int


def create_app(database_path: str | Path | None = None) -> FastAPI:
    """Izveidot lietotni ar norādāmu SQLite datubāzes failu."""
    path = database_path or os.getenv(
        "SPELE_DB", str(API_DIR.parent / "data" / "scores.db")
    )
    database = Database(path)

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        """Sagatavot SQLite pirms pieprasījumu saņemšanas."""
        database.initialize()
        yield

    app = FastAPI(
        title="Čūska kurjers API",
        description="Spēles rezultāti un spēlētāju statistika.",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.mount(
        "/static", StaticFiles(directory=API_DIR / "static"), name="static"
    )
    templates = Jinja2Templates(directory=API_DIR / "templates")

    @app.post(
        "/scores",
        status_code=201,
        response_model=ScoreOutput,
        summary="Saglabāt rezultātu",
    )
    def save_score(result: ScoreInput) -> dict:
        """Saglabāt pārbaudīto rezultātu un atgriezt datubāzes ierakstu."""
        return database.add_score(result.name, result.score)

    @app.get(
        "/scores/top",
        response_model=list[ScoreOutput],
        summary="Labākie desmit rezultāti",
    )
    def top_scores() -> list[dict]:
        """Atgriezt desmit labākos rezultātus."""
        return database.top_scores()

    @app.get(
        "/players/{name}/stats",
        response_model=PlayerStats,
        summary="Spēlētāja statistika",
    )
    def player_stats(name: str) -> dict:
        """Atgriezt statistiku vai kļūdu 404, ja spēlētājs nav atrasts."""
        stats = database.player_stats(name)
        if stats is None:
            raise HTTPException(404, detail="Spēlētājs nav atrasts.")
        return stats

    @app.get("/", response_class=HTMLResponse, summary="Rezultātu tabula")
    def home(request: Request) -> HTMLResponse:
        """Parādīt labākos rezultātus ar Jinja veidni."""
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"scores": database.top_scores()},
        )

    @app.get("/rules", response_class=HTMLResponse, summary="Spēles noteikumi")
    def rules(request: Request) -> HTMLResponse:
        """Parādīt spēles aprakstu un vadību."""
        return templates.TemplateResponse(request=request, name="rules.html")

    @app.get(
        "/players/{name}",
        response_class=HTMLResponse,
        summary="Spēlētāja profils",
    )
    def profile(request: Request, name: str) -> HTMLResponse:
        """Parādīt spēlētāja profilu vai saprotamu kļūdas lapu."""
        stats = database.player_stats(name)
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={"stats": stats, "player_name": name},
            status_code=200 if stats else 404,
        )

    return app


app = create_app()
