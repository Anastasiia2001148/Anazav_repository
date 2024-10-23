from typing import Optional

from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date, timedelta
from src.database.db import get_db

from src.schemas.schemas import ContactResponse, ContactCreate
from src.models.models import Contact, Base
from src.database.db import sessionmanager
from sqlalchemy import text
from sqlalchemy import extract

from src.repository.repository import get_contacts, get_contact, update_contact, delete_contact

app = FastAPI()

router = APIRouter()

@router.get('/')
def index():
    return {'message': 'Homework 11'}

app.include_router(router, include_in_schema=False)

@app.on_event("startup")
async def startup():
    async with sessionmanager._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/contacts/", response_model=ContactResponse)
async def create_contact(contact_data: ContactCreate, db: AsyncSession = Depends(get_db)):
    new_contact = Contact(**contact_data.dict())
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact


@app.get("/contacts/", response_model=list[ContactResponse])
async def read_contacts(limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await get_contacts(db, limit=limit, offset=offset)


@app.get("/contacts/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    db_contact = await get_contact(contact_id, db)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@app.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact_(contact_id: int, contact: ContactCreate, db: AsyncSession = Depends(get_db)):
    db_contact = await update_contact(contact_id, contact, db)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_(contact_id: int, db: AsyncSession = Depends(get_db)):
    db_contact = await delete_contact(contact_id, db)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")


@app.get("/contacts/search/", response_model=list[ContactResponse])
async def search_contacts(
        first_name: Optional[str] = Query(None),
        last_name: Optional[str] = Query(None),
        email: Optional[str] = Query(None),
        db: AsyncSession = Depends(get_db)
):
    query = select(Contact)

    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    result = await db.execute(query)
    return result.scalars().all()


@app.get("/contacts/birthdays/", response_model=list[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    today = date.today()
    upcoming_date = today + timedelta(days=7)
    query = select(Contact).filter(
(extract('month', Contact.birthday) == today.month) & (extract('day', Contact.birthday) >= today.day),    (extract('month', Contact.birthday) == upcoming_date.month) & (
extract('day', Contact.birthday) <= upcoming_date.day))

    result = await db.execute(query)
    return result.scalars().all()


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
