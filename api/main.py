"""Serveris: saņem spēles rezultātus un parāda mājaslapu.

Spēle saņem JSON datus, bet pārlūks saņem gatavas HTML lapas.
Abos gadījumos rezultātus nolasa no tās pašas SQLite datubāzes.
"""

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
    """Noteikumi datiem, kurus spēle nosūta uz POST /scores."""

    # extra="forbid" noraida papildu laukus, piemēram, admin.
    # strict=True nepieņem tekstu "20" skaitļa 20 vietā.
    # Nederīgus datus FastAPI noraida ar kodu 422 pirms saglabāšanas funkcijas.
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=24, strict=True)
    score: int = Field(ge=0, le=1_000_000_000, strict=True)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        """Pārbaudīt vārdu pēc tiem pašiem noteikumiem, kurus lieto spēle."""
        # @field_validator liek Pydantic izsaukt šo pārbaudi laukam name.
        return validate_name(value)


class ScoreOutput(ScoreInput):
    """Servera atbilde: vārds un punkti, papildus ieraksta ID un UTC laiks."""

    # Vārdu un punktus manto no ScoreInput; šie abi lauki nāk no datubāzes.
    id: int
    created_at: str


class PlayerStats(BaseModel):
    """Spēlētāja vārds, saglabāto spēļu skaits un labākais rezultāts."""

    name: str
    games: int
    best_score: int


def create_app(database_path: str | Path | None = None) -> FastAPI:
    """Sagatavot serveri, datubāzi, API adreses un mājaslapas adreses."""
    # Parasti lieto projekta data/scores.db; SPELE_DB ļauj izvēlēties citu failu.
    # Testi padod savu pagaidu failu, lai nemainītu īstos spēles rezultātus.
    path = database_path or os.getenv(
        "SPELE_DB", str(API_DIR.parent / "data" / "scores.db")
    )
    database = Database(path)

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        """Servera palaišanas brīdī izveidot datubāzi, ja tās vēl nav."""
        database.initialize()
        # Viss pirms yield notiek palaižot serveri. Pie yield tas ir gatavs
        # saņemt pieprasījumus; kods pēc yield izpildītos servera apturēšanas laikā.
        yield

    app = FastAPI(
        title="Čūska kurjers API",
        description="Spēles rezultāti un spēlētāju statistika.",
        version="1.0.0",
        lifespan=lifespan,
    )
    # /static adresē pārlūks var saņemt style.css un citus statiskos failus.
    # API_DIR atrod failus arī tad, ja serveri palaiž no citas darba mapes.
    app.mount(
        "/static", StaticFiles(directory=API_DIR / "static"), name="static"
    )
    # Jinja ievieto datubāzes rezultātus HTML veidnēs no templates mapes.
    templates = Jinja2Templates(directory=API_DIR / "templates")

    # @app.post un @app.get savieno adresi ar funkciju, kas to apstrādā.
    # Pirmās trīs adreses atgriež JSON datus spēlei vai API lietotājam.
    @app.post(
        "/scores",
        status_code=201,
        response_model=ScoreOutput,
        summary="Saglabāt rezultātu",
    )
    def save_score(result: ScoreInput) -> dict:
        """Saglabāt pārbaudīto rezultātu un atgriezt datubāzes ierakstu."""
        # Šeit dati jau ir pārbaudīti ar ScoreInput.
        # add_score saglabā tos SQLite, bet FastAPI izveido JSON atbildi ar kodu 201.
        return database.add_score(result.name, result.score)

    @app.get(
        "/scores/top",
        response_model=list[ScoreOutput],
        summary="Labākie desmit rezultāti",
    )
    def top_scores() -> list[dict]:
        """Atgriezt desmit labākos rezultātus."""
        # Tā ir labāko partiju tabula: vienam vārdam var būt vairāki ieraksti.
        return database.top_scores()

    @app.get(
        "/players/{name}/stats",
        response_model=PlayerStats,
        summary="Spēlētāja statistika",
    )
    def player_stats(name: str) -> dict:
        """Atgriezt statistiku vai kļūdu 404, ja spēlētājs nav atrasts."""
        # {name} adresē kļūst par argumentu, piemēram, /players/Anna/stats.
        stats = database.player_stats(name)
        if stats is None:
            raise HTTPException(404, detail="Spēlētājs nav atrasts.")
        return stats

    # Tālāk ir pārlūka lapas: tās atgriež HTML, nevis tikai JSON datus.
    @app.get("/", response_class=HTMLResponse, summary="Rezultātu tabula")
    def home(request: Request) -> HTMLResponse:
        """Parādīt labākos rezultātus ar Jinja veidni."""
        # context nodod sarakstu index.html veidnei ar nosaukumu scores.
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


# Uvicorn palaiž šo objektu ar komandu: uvicorn api.main:app.
app = create_app()
