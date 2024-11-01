from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.routes.routes import router as contacts_router
from src.routes.auth import router as auth_router
from src.database.db import get_db
from src.models.models import Base
from src.database.db import sessionmanager
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()



app.include_router(auth_router, prefix="/auth")
app.include_router(contacts_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with sessionmanager._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



@app.get("/")
def index():
    return {"message": "Homework 11"}

@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")




