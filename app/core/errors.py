from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class EduStartException(Exception):
    """Base exception for EduStart application"""
    def __init__(self, message: str, code: str = "EDUSTART_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AuthenticationError(EduStartException):
    """Authentication related errors"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR")


class AuthorizationError(EduStartException):
    """Authorization related errors"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "AUTHZ_ERROR")


class ResourceNotFoundError(EduStartException):
    """Resource not found errors"""
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", "NOT_FOUND")


class ValidationException(EduStartException):
    """Validation errors"""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class DatabaseError(EduStartException):
    """Database operation errors"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DB_ERROR")


def add_exception_handlers(app: FastAPI):
    """
    Add custom exception handlers to FastAPI app
    """
    
    @app.exception_handler(EduStartException)
    async def edustart_exception_handler(request: Request, exc: EduStartException):
        logger.error(f"EduStart exception: {exc.code} - {exc.message}")
        
        status_code_map = {
            "AUTH_ERROR": status.HTTP_401_UNAUTHORIZED,
            "AUTHZ_ERROR": status.HTTP_403_FORBIDDEN,
            "NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
            "DB_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
        
        return JSONResponse(
            status_code=status_code_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR),
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error: {exc.errors()}")
        
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid input data",
                    "details": errors
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                }
            }
        )