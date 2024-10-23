from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.models import Contact
from src.schemas.schemas import ContactCreate

async def create_contact(contact: ContactCreate, db: AsyncSession):
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact

async def get_contacts(db: AsyncSession, limit: int = 10, offset: int = 0):
    result = await db.execute(select(Contact).offset(offset).limit(limit))
    return result.scalars().all()

async def get_contact(contact_id: int, db: AsyncSession):
    result = await db.execute(select(Contact).filter(Contact.id == contact_id))
    return result.scalar_one_or_none()

async def update_contact(contact_id: int, contact: ContactCreate, db: AsyncSession):
    db_contact = await get_contact(contact_id, db)
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        await db.commit()
        await db.refresh(db_contact)
        return db_contact
    return None

async def delete_contact(contact_id: int, db: AsyncSession):
    db_contact = await get_contact(contact_id, db)
    if db_contact:
        await db.delete(db_contact)
        await db.commit()
        return db_contact
    return None