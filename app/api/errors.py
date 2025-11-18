from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValidationError)
    async def handle_validation_error(_: Request, exc: ValidationError) -> JSONResponse:  # type: ignore[override]
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(ValueError)
    async def handle_value_error(_: Request, exc: ValueError) -> JSONResponse:  # type: ignore[override]
        return JSONResponse(status_code=400, content={"detail": str(exc)})
