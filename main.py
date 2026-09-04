from fastapi import FastAPI
from app.config.database import Base, engine
from app.models.user import User

def create_application():
     # Create database tables
    print("Tables:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)

    application = FastAPI()
    return application


app = create_application()

@app.get("/")
async def root():
    return {"message": "Hello nvr!"}

