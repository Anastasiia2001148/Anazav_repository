import uuid
from urllib.parse import urlparse, unquote
from typing import List
import cloudinary
import cloudinary.uploader
from fastapi import Body
from fastapi import APIRouter, Depends, status, Path, HTTPException, UploadFile, File, Query,Form
from fastapi_limiter.depends import RateLimiter


from src.entity.models import User, Photo,Tag
from src.schemas.photos import PhotosSchemaResponse, PhotoValidationSchema,PhotoResponse,PhotoCreate

from src.repository import photos as repositories_photos
from src.services.auth import auth_service
from src.conf.config import config
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.auth import auth_service
from src.database.db import get_db
from src.services.cloudinary import upload_image_to_cloudinary,generate_transformed_image_url



routerPhotos = APIRouter(prefix="/photos", tags=["photos"])

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)



@routerPhotos.post("/", response_model=PhotoResponse)
async def create_photo(
        description: str = Form(...),
        tags: List[str] = Form(...),
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_db),
        user=Depends(auth_service.get_current_user),
):
    """
       Creates a new photo and uploads it to Cloudinary. The photo is then associated with tags and saved in the database.

       Args:
           description (str): A description of the photo.
           tags (List[str]): A list of tags to associate with the photo. Maximum of 5 tags are allowed.
           file (UploadFile): The file to upload as the photo.
           session (AsyncSession): The database session used to interact with the database.
           user (User): The currently authenticated user making the request.

       Raises:
           HTTPException: If more than 5 tags are provided.

       Returns:
           dict: A dictionary containing the following fields:
               - id (int): The ID of the newly created photo.
               - user_id (int): The ID of the user who uploaded the photo.
               - description (str): The description of the photo.
               - tags (List[str]): A list of tags associated with the photo.
               - image (str): The URL of the uploaded image in Cloudinary.
       """
    tags = tags[0].split(",") if isinstance(tags, list) else tags.split(",")

    if len(tags) > 5:
        raise HTTPException(status_code=400, detail="You can add up to 5 tags.")

    tags = list(set(tags))

    image_url, public_id = await upload_image_to_cloudinary(file)

    new_photo = Photo(
        image=public_id,
        description=description,
        user_id=user.id,
    )

    session.add(new_photo)

    for tag_name in tags:
        tag_result = await session.execute(select(Tag).where(Tag.name == tag_name))
        tag = tag_result.scalars().first()

        if not tag:
            tag = Tag(name=tag_name)
            session.add(tag)

        new_photo.photo_tags.append(tag)

    await session.commit()
    await session.refresh(new_photo)

    return {
        "id": new_photo.id,
        "user_id": new_photo.user_id,
        "description": new_photo.description,
        "tags": tags,
        "image": image_url
    }


@routerPhotos.delete(
    "/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a photo",
    description="Deletes a photo from the database",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def delete_photo(
        photo_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    """
    Deletes a photo from the database and from Cloudinary.

    Args:
        photo_id (int): The ID of the photo to delete.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user, obtained through authentication services.

    Raises:
        HTTPException: If the photo does not exist, or the user does not have permission to delete it.
    """
    res = await repositories_photos.read_photo(photo_id, db)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    if current_user.role == "admin" or res.user_id == current_user.id:
        image_to_delete = res.image
        parsed_url = urlparse(image_to_delete)

        print(f"Parsed URL path: {parsed_url.path}")

        path_parts = parsed_url.path.split('/')


        if len(path_parts) >= 1:
            public_id = path_parts[-1].split('.')[0]
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL format for public_id")


        try:
            result = cloudinary.uploader.destroy(public_id=public_id, invalidate=True)
            if result["result"] == "ok":
                await repositories_photos.delete_photo(photo_id, db)
            elif result["result"] == "not found":
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found in Cloudinary")
            else:
                raise Exception(f"Error deleting photo from Cloudinary: {result['result']}")
        except cloudinary.exceptions.Error as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Cloudinary error: {str(e)}")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission")
@routerPhotos.put(
    "/{photo_id}",
    response_model=PhotosSchemaResponse,
    summary="Update description of a photo by ID",
    description="Updates description of a photo in the database by its ID",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def update_photo(
        photo_id: int,
        description: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    """
    Updates description of a photo in the database by its ID.

    Args:
        photo_id (int): The ID of the photo to update.
        description (str): The new description of the photo.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user, obtained through authentication services.

    Raises:
        HTTPException: If the photo does not exist, or the user does not have permission to update it.

    Returns:
        PhotosSchemaResponse: The updated photo.
    """
    res = await repositories_photos.read_photo(photo_id, db)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    if current_user.role == "admin" or res.user_id == current_user.id:
        update_photo = await repositories_photos.update_photo(photo_id, description, db)
        return update_photo
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission")


@routerPhotos.get(
    "/{photo_id}",
    response_model=PhotosSchemaResponse,
    summary="Retrieve a photo by ID",
    description="Gets a photo from the database by its ID",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def read_photo(
        photo_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    """
    Gets a photo from the database by its ID.

    Args:
        photo_id (int): The ID of the photo to retrieve.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user, obtained through authentication services.

    Raises:
        HTTPException: If the photo does not exist, or the user does not have permission to read it.

    Returns:
        PhotosSchemaResponse: The retrieved photo.
    """
    photo = await repositories_photos.read_photo(photo_id, db)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    # if photo.user_id == current_user.id or current_user.role == "admin":
    return photo
    # else:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission")


@routerPhotos.get(
    "/",
    response_model=list[PhotoValidationSchema],
    summary="Retrieve all photos",
    description="Gets all photos from the database",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def read_photos(
        limit: int = Query(default=10, ge=0, le=50, description="The maximum number of photos to return"),
        offset: int = Query(default=0, ge=0, description="The offset from which to start returning photos"),
        all_photos: bool = Query(default=False,
                                 description="Flag to get all photos from the database; default (False) is only photos of the current user"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    """
    Gets all photos from the database.

    Args:
        limit (int): The maximum number of photos to return. Defaults to 10.
        offset (int): The offset from which to start returning photos. Defaults to 0.
        all_photos (bool): A flag to get all photos from the database. Defaults to False - only photos of the current user.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user, obtained through authentication services.

    Returns:
        list[PhotosSchemaResponse]: A list of photos that match the provided filters.
    """
    if not all_photos:
        id_user = current_user.id
    else:
        id_user = 0

    photos = await repositories_photos.read_all_photos(limit=limit, offset=offset, db=db, user_id=id_user)

    # Проверка и корректировка значений description
    for photo in photos:
        if not photo.description:
            photo.description = "No description provided"  # Дефолтное описание, если пустое

    return photos

@routerPhotos.get("/{photo_id}/transform")
async def transform_photo(
        photo_id: int,
        width: int = 300,
        height: int = 300,
        crop: str = "fill",
        angle: int = 0,
        effect: str = None,
        quality: int = None,
        format: str = None,
        user=Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    """
        Transforms a photo by applying various modifications such as resizing, cropping, rotating, and adding effects.

        Args:
            photo_id (int): The ID of the photo to transform.
            width (int): The width of the transformed image (default is 300).
            height (int): The height of the transformed image (default is 300).
            crop (str): The crop mode (default is 'fill'). Other options can include 'scale', 'fit', etc.
            angle (int): The angle to rotate the image (default is 0).
            effect (str, optional): The name of the effect to apply (e.g., 'grayscale'). If not provided, no effect is applied.
            quality (int, optional): The quality of the transformed image (default is None).
            format (str, optional): The format to convert the image to (e.g., 'jpeg'). If not provided, no conversion is applied.
            user (User): The currently authenticated user.
            session (AsyncSession): The database session for querying the photo.

        Raises:
            HTTPException:
                - 404: If the photo with the given ID is not found.
                - 403: If the current user does not have permission to transform the photo.

        Returns:
            dict: A dictionary containing the transformed image URL.
                - transformed_url (str): The URL of the transformed image.
        """

    photo_result = await session.execute(select(Photo).where(Photo.id == photo_id))
    photo = photo_result.scalars().first()

    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    if photo.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")


    transformations = {"width": width, "height": height, "crop": crop}

    if angle:
        transformations["angle"] = angle
    if effect:
        transformations["effect"] = effect
    if quality:
        transformations["quality"] = quality
    if format:
        transformations["format"] = format


    transformed_url = generate_transformed_image_url(photo.image.split("/")[-1].split(".")[0], transformations)
    return {"transformed_url": transformed_url}