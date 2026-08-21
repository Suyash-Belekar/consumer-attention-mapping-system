from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.api import auth, stores, analytics, intelligence, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Consumer Attention Mapping System",
    description="Milestone 3 - Behavioral Intelligence & Optimization",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(analytics.router)
app.include_router(intelligence.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {"message": "Consumer Attention Mapping System API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
