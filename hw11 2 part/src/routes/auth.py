from asyncio.log import logger

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.schemas.user import UserCreate, Token
from src.models.models import User
from src.utils.auth import verify_password
from src.utils.check import create_access_token,create_refresh_token
from src.repository.repository import get_user_by_email
from fastapi.security import OAuth2PasswordRequestForm
from src.utils.auth import pwd_context
router = APIRouter()


from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        existing_user = await get_user_by_email(user_data.email, db)
        if existing_user:
            logger.warning(f"User already exists: {user_data.email}")
            raise HTTPException(status_code=409, detail="User with this email already exists.")

        hashed_password = pwd_context.hash(user_data.password)
        new_user = User(email=user_data.email, hashed_password=hashed_password)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        access_token = create_access_token(data={"sub": new_user.email})
        refresh_token = create_refresh_token(data={"sub": new_user.email})

        return JSONResponse(
            status_code=201,
            content={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "email": new_user.email,
                    "id": new_user.id,
                }
            }
        )

    except IntegrityError:
        await db.rollback()
        logger.error(f"Error {user_data.email} already exists.")
        raise HTTPException(status_code=409, detail="User with this email already exists.")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(form_data.username, db)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, 'refresh_token': refresh_token, "token_type": "bearer"}