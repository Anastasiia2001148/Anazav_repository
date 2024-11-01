from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.models import Contact, User
from src.schemas.schemas import ContactCreate

import logging

logger = logging.getLogger(__name__)

async def get_user_by_email(email: str, db: AsyncSession) -> User:
    logger.debug(f"Запрос пользователя по email: {email}")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    return user

async def get_contacts(db: AsyncSession, user_id: int, limit: int = 10, offset: int = 0):
    query = select(Contact).filter(Contact.user_id == user_id).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_contact(contact_id: int, user: User, db: AsyncSession):
    try:
        query = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error {contact_id} for {user.id}: {e}")
        return None

async def update_contact(contact_id: int, contact: ContactCreate, user: User, db: AsyncSession):
    try:
        db_contact = await get_contact(contact_id, user, db)
        if db_contact:
            for key, value in contact.dict().items():
                setattr(db_contact, key, value)
            await db.commit()
            await db.refresh(db_contact)
            return db_contact
        else:
            logger.warning(f"Contact {contact_id} not found for {user.id}")
            return None
    except Exception as e:
        logger.error(f"Error {contact_id} for {user.id}: {e}")
        return None

async def delete_contact(contact_id: int, user: User, db: AsyncSession):
    try:
        db_contact = await get_contact(contact_id, user, db)
        if db_contact:
            await db.delete(db_contact)
            await db.commit()
            return db_contact
        else:
            logger.warning(f"Contatc  {contact_id} not founf for {user.id}")
            return None
    except Exception as e:
        logger.error(f"Error  {contact_id} for {user.id}: {e}")
        return None