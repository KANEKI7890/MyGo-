from fastapi import APIRouter

from app.api.routes import ai, auth, dashboard, events, practices, schedule, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(practices.router)
api_router.include_router(events.router)
api_router.include_router(schedule.router)
api_router.include_router(dashboard.router)
api_router.include_router(ai.router)
