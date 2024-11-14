from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from src.routes import users
from src.routes.routes import router as contacts_router
from src.routes.auth import router as auth_router, api_router
from src.database.db import get_db
from src.models.models import Base
from src.database.db import sessionmanager
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from src.conf.config import config
from fastapi_limiter import FastAPILimiter

app = FastAPI()

app.include_router(api_router, prefix="/api/auth")
app.include_router(auth_router, prefix="/auth")
app.include_router(contacts_router)
app.include_router(users.router, prefix="/api/users")

@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(r)

origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with sessionmanager._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

templates = Jinja2Templates(directory="src/templates")

@app.get("/")
def index():
    return {"message": "Homework 13"}

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




