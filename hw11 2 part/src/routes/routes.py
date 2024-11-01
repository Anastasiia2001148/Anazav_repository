from asyncio.log import logger
from typing import Optional

from fastapi import  APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date, timedelta
from src.database.db import get_db

from src.schemas.schemas import ContactResponse, ContactCreate
from src.models.models import Contact, User
from sqlalchemy import extract

from src.repository.repository import get_contacts, get_contact
from src.utils.dependencies import get_current_user

router = APIRouter()

@router.post("/contacts/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact_data: ContactCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_contact = Contact(**contact_data.dict(), user_id=current_user.id)
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact

@router.get("/contacts/", response_model=list[ContactResponse])
async def read_contacts(limit: int = 10, offset: int = 0, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_contacts(db, user_id=current_user.id, limit=limit, offset=offset)


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, current_user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    db_contact = await get_contact(contact_id, current_user, db)
    if db_contact is None or db_contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact_(
    contact_id: int,
    contact: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    db_contact = await get_contact(contact_id, current_user, db)


    if db_contact is None or db_contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")


    for key, value in contact.dict().items():
        setattr(db_contact, key, value)


    try:
        await db.commit()
        await db.refresh(db_contact)
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при обновлении контакта {contact_id} для пользователя {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обновлении контакта")

    return db_contact

async def get_contact(contact_id: int, user: User, db: AsyncSession):
    try:

        query = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Ошибка при получении контакта {contact_id} для пользователя {user.id}: {e}")
        return None

@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_(contact_id: int, current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    db_contact = await get_contact(contact_id, db)
    if db_contact is None or db_contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")

    await db.delete(db_contact)
    await db.commit()

@router.get("/contacts/search/", response_model=list[ContactResponse])
async def search_contacts(
        first_name: Optional[str] = Query(None),
        last_name: Optional[str] = Query(None),
        email: Optional[str] = Query(None),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    query = select(Contact).filter(Contact.user_id == current_user.id)

    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/contacts/birthdays/", response_model=list[ContactResponse])
async def get_upcoming_birthdays(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    today = date.today()
    upcoming_date = today + timedelta(days=7)
    query = select(Contact).filter( Contact.user_id == current_user.id,
    ((extract('month', Contact.birthday) == today.month) &(extract('day', Contact.birthday) >= today.day)) | ((extract('month', Contact.birthday) == upcoming_date.month) & (extract('day', Contact.birthday) <= upcoming_date.day)))

    result = await db.execute(query)
    return result.scalars().all()