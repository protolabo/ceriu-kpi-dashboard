from fastapi import APIRouter
from app.endpoints import analytics, mailchimp

"""
This module centralizes and aggregates the API routes into a single unified router.
"""

router = APIRouter()
router.include_router(analytics.router, tags=["analytics"])
router.include_router(mailchimp.router)