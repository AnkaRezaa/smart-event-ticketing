from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.config import settings
from app.database.connection import engine, Base, SessionLocal
from app.database.models import User, UserRole, Event
from app.security.password import hash_password
from app.security.session import get_current_user_from_session

from app.routes.auth import router as auth_router
from app.routes.events import router as events_router
from app.routes.participant import router as participant_router
from app.routes.checkin import router as checkin_router
from app.routes.admin import router as admin_router
from app.routes.cv_lab import router as cv_lab_router

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Smart Event Ticketing System with Biometric Facial Authentication (HOG, KNN, PSO)",
    version="1.0.0"
)

# Mount static assets
app.mount("/static/results", StaticFiles(directory="research/results"), name="research_results")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Register routers
app.include_router(auth_router)
app.include_router(events_router)
app.include_router(participant_router)
app.include_router(checkin_router)
app.include_router(admin_router)
app.include_router(cv_lab_router)

@app.on_event("startup")
def on_startup():
    """Initializes tables and seeds default admin and demo event if database is new."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@smartticket.com").first()
        if not admin:
            admin = User(
                name="Administrator",
                email="admin@smartticket.com",
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN
            )
            db.add(admin)

        # Check if demo operator exists
        operator = db.query(User).filter(User.email == "operator@smartticket.com").first()
        if not operator:
            operator = User(
                name="Venue Turnstile Operator",
                email="operator@smartticket.com",
                password_hash=hash_password("operator123"),
                role=UserRole.OPERATOR
            )
            db.add(operator)

        # Seed initial demo event if none exist
        if db.query(Event).count() == 0:
            now = datetime.utcnow()
            demo_event = Event(
                title="International AI & Music Festival 2026",
                description="A premier live music and technology festival featuring top international artists. Protected with two-stage biometric QR and facial verification.",
                location="Grand Arena Stadium, Main Stage",
                start_at=now + timedelta(days=14),
                end_at=now + timedelta(days=14, hours=6),
                registration_open_at=now - timedelta(days=1),
                registration_close_at=now + timedelta(days=13),
                checkin_open_at=now + timedelta(days=14, hours=-3),
                checkin_close_at=now + timedelta(days=14, hours=5),
                capacity=500,
                status="ACTIVE"
            )
            db.add(demo_event)

        db.commit()
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    user = get_current_user_from_session(request)
    return templates.TemplateResponse(
        request=request,
        name="public/landing.html",
        context={"current_user": user}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.APP_DEBUG)

