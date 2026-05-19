from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

try:
    from backend.routes.auth import router as auth_router
    from backend.routes.dashboard import router as dashboard_router
    from backend.routes.predict import router as predict_router
    from backend.routes.report import router as report_router
    from backend.routes.upload import router as upload_router
    from backend.utils.auth import seed_demo_user
    from backend.utils.database import init_db
    from backend.utils.preprocess import CHART_DIR, ensure_directories
except ModuleNotFoundError:
    from routes.auth import router as auth_router
    from routes.dashboard import router as dashboard_router
    from routes.predict import router as predict_router
    from routes.report import router as report_router
    from routes.upload import router as upload_router
    from utils.auth import seed_demo_user
    from utils.database import init_db
    from utils.preprocess import CHART_DIR, ensure_directories

ensure_directories()
init_db()
seed_demo_user()

app = FastAPI(title="FAILSAFE API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(report_router)
app.include_router(upload_router)
app.include_router(predict_router)
app.include_router(dashboard_router)
app.include_router(auth_router)

app.mount(
    "/charts",
    StaticFiles(
        directory=str(CHART_DIR)
    ),
    name="charts"
)

@app.get("/")
def home():
    return {
        "project": "FAILSAFE",
        "status": "running",
        "docs": "/docs",
    }
