from fastapi import APIRouter, UploadFile, HTTPException, Depends
import cloudinary
import cloudinary.uploader
from src.database.db import get_db
from src.models.models import User
from sqlalchemy.future import select
from src.conf.config import config
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True)


@router.patch("/api/users/avatar", tags=['users'])
async def update_avatar(file: UploadFile, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    try:
        result = await db.execute(select(User).filter(User.email == current_user.email))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")


        upload_result = cloudinary.uploader.upload(file.file, folder="avatars/")

        avatar_url = upload_result.get("secure_url")
        user.avatar = avatar_url
        await db.commit()

        return {"message": "Avatar updated successfully", "avatar_url": avatar_url}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
