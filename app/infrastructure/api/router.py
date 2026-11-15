from fastapi import APIRouter

from .endpoints import invoice

router = APIRouter(prefix="/api")

router.include_router(invoice.router)
