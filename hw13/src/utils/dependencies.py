from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.db import get_db
from src.models.models import User
from src.utils.security import oauth2_scheme
from jose import JWTError, jwt
from src.conf.config import config


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY_JWT, algorithms=[config.ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    query = select(User).filter(User.email == user_email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user
