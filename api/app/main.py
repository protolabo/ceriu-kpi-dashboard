import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.endpoints.router import router
from app.config.settings import settings

description = """
API REST pour faciliter l'intégration de données provenant de services tiers (GA4, Mailchimp, Vimeo) dans Power BI.
"""

logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log") if settings.ENVIRONMENT == "production" else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    logger.info(f"Démarrage de {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Base URL: {settings.BASE_URL}")
    logger.info(f"CORS Origins: {settings.BACKEND_CORS_ORIGINS}")
    
    yield
    
    # Shutdown
    logger.info("Arrêt de l'application")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=description,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
    expose_headers=["X-Total-Count", "X-Request-ID"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log toutes les requêtes HTTP"""
    logger.info(f"{request.method} {request.url.path} - Client: {request.client.host}")
    
    try:
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} - Status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"{request.method} {request.url.path} - Error: {str(e)}")
        raise


# ========================================
# ROUTES
# ========================================

@app.get("/", tags=["health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "base_url": settings.BASE_URL,
    }

# Inclusion du router principal
app.include_router(router, prefix=settings.API_V1_STR)

# ========================================
# POINT D'ENTRÉE
# ========================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.ENVIRONMENT != "production",
        log_level=logging.INFO,
        access_log=True,
    )
