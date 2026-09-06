from fastapi import FastAPI
from app.config.database import Base, engine
from app.models.user import User
from app.routes import user

def create_application():
     # Create database tables for  sqlalchmey to recognie
    # print("Tables:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)

    application = FastAPI()
    # routes
    application.include_router(user.user_router)
    application.include_router(user.guest_router)
    return application


app = create_application()

@app.get("/")
async def root():
    return {"message": "Hello nvr!"}

