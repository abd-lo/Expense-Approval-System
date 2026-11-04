from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models
from .routers import auth

# Creates the tables in PostgreSQL upon startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Approval System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Authentication router
app.include_router(auth.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Database tables created successfully"}