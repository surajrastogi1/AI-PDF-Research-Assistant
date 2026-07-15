from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_db_and_tables
from app.routers import auth, projects, analytics

app = FastAPI(title="ResearchMind Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your Vite frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Registering our modular routers cleanly
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {"message": "API Running"}

