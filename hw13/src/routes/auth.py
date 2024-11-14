from asyncio.log import logger

from fastapi import APIRouter, status

from src.database.db import get_db
from src.repository import repository
from fastapi_limiter.depends import RateLimiter
from src.schemas.user import UserCreate, Token, RequestEmail
from src.models.models import User
from src.utils.auth import verify_password
from src.utils.check import create_access_token, create_refresh_token, auth_service
from src.repository.repository import get_user_by_email
from fastapi.security import OAuth2PasswordRequestForm
from src.utils.auth import pwd_context
from src.utils.email import send_email

from fastapi import HTTPException, BackgroundTasks, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse


router = APIRouter()
api_router = APIRouter()

@router.post("/register", response_model=Token,dependencies=[Depends(RateLimiter(times=1, seconds=20))], tags=["auth"])
async def register(user_data: UserCreate, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(user_data.email, db)
    if existing_user:
        raise HTTPException(status_code=409, detail="User with this email already exists.")

    try:
        hashed_password = pwd_context.hash(user_data.password)

        new_user = User(email=user_data.email, hashed_password=hashed_password, username=user_data.username)

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        access_token = create_access_token(data={"sub": new_user.email})
        refresh_token = create_refresh_token(data={"sub": new_user.email})

        bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))

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

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", dependencies=[Depends(RateLimiter(times=1, seconds=5))],tags=["auth"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(form_data.username, db)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not confirmed",
        )
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, 'refresh_token': refresh_token, "token_type": "bearer"}


@api_router.get('/confirmed_email/{token}',dependencies=[Depends(RateLimiter(times=1, seconds=20))],tags=["auth"])
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository.confirmed_email(email, db)
    return {"message": "Email confirmed"}




@router.post('/request_email',dependencies=[Depends(RateLimiter(times=1, seconds=20))],tags=["auth"])
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    user = await repository.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


