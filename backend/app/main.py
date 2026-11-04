from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models
from .routers import auth, expenses
from app.seed import seed_initial_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Ensure all database tables exist
    Base.metadata.create_all(bind=engine)
    # 2. Seed initial demo users if not present
    seed_initial_data()
    yield


app = FastAPI(title="Expense Approval System", lifespan=lifespan)

origins = [
    "http://localhost:5173",  # Default Vite dev server port
    "http://localhost:3000",  # Standard React port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Authentication and Expense routers
app.include_router(auth.router)
app.include_router(expenses.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Database tables created and app is healthy"}