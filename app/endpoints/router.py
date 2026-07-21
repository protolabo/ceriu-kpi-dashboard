from fastapi import APIRouter
from app.endpoints import analytics, mailchimp, vimeo, facebook

"""
This module centralizes and aggregates the API routes into a single unified router.
"""

router = APIRouter()
router.include_router(analytics.router, tags=["analytics"])
router.include_router(mailchimp.router)
router.include_router(vimeo.router)
router.include_router(facebook.router)