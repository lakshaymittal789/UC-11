from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from profile_summary.form_routes import router as form_summary_router
from profile_summary.notes_routes import router as notes_summary_router
from profile_summary.routes import router as profile_summary_router

app = FastAPI(title="Homecare AI Profile Summary API")
app.include_router(profile_summary_router)
app.include_router(form_summary_router)
app.include_router(notes_summary_router)

FRONTEND_DIR = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
async def frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
