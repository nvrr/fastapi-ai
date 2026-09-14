from fastapi import FastAPI
from app.config.database import Base, engine
from app.models.user import User
from app.routes import user
from app.routes import product

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

def create_application():
     # Create database tables for  sqlalchmey to recognie
    # print("Tables:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)

    application = FastAPI()
    # routes
    application.include_router(user.user_router)
    application.include_router(user.guest_router)
    application.include_router(user.auth_router)
    application.include_router(product.product_router)
    return application


app = create_application()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = []

    for error in exc.errors():
        field = ".".join(
            str(location)
            for location in error["loc"]
            if location != "body"
        )

        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation failed",
            "errors": errors,
        },
    )


@app.get("/")
async def root():
    return {"message": "Hello nvr!"}

