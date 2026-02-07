from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
import logging

from app.core.config import settings
from app.core.errors import add_exception_handlers
from app.api.v1.router import api_router
from app.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Path to React build directory
UI_DIR = Path(__file__).parent.parent / "ui" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting EduStart Backend API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down EduStart Backend API...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API Backend untuk Aplikasi Pembelajaran EduStart",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
add_exception_handlers(app)

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


# Serve React SPA static files (must be after API routes)
if UI_DIR.exists():
    # Mount static assets (JS, CSS, images, etc.)
    assets_dir = UI_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="static-assets")
    
    # Serve other static files from ui/dist (favicon, etc.)
    @app.get("/vite.svg", include_in_schema=False)
    @app.get("/favicon.ico", include_in_schema=False)
    async def serve_favicon():
        favicon = UI_DIR / "vite.svg"
        if favicon.exists():
            return FileResponse(favicon)
        return FileResponse(UI_DIR / "index.html")
    
    # Catch-all route for SPA - serves index.html for client-side routing
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Serve React SPA for all non-API routes"""
        # Check if it's a file request in dist
        file_path = UI_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Otherwise serve index.html for SPA routing
        return FileResponse(UI_DIR / "index.html")
else:
    # If UI is not built, serve API info at root
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint"""
        return {
            "message": "Welcome to EduStart API",
            "version": settings.VERSION,
            "docs": "/docs" if settings.DEBUG else "Disabled in production",
            "note": "Build the UI with 'npm run build' in ui/ to serve the frontend"
        }