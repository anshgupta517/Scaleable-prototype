from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional

from database import get_db, Item, create_db_tables

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    is_offered: bool = False

class ItemCreate(ItemBase):
    pass 

class ItemUpdate(ItemBase):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    is_offered: Optional[bool] = None

class ItemInDB(ItemBase):
    id: int 
    class Config:
        orm_mode = True 

app = FastAPI()
@app.on_event("startup")
async def startup_event():
    print("Application starting up... Creating database tables (if they don't exist).")
    await create_db_tables()
    print("Database tables ensured.")



# Create an Item
@app.post("/items/", response_model=ItemInDB, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = Item(**item.dict())
    db.add(db_item) 
    await db.commit()
    await db.refresh(db_item) 
    return db_item

@app.get("/items/", response_model=List[ItemInDB])
async def read_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).offset(skip).limit(limit))
    items = result.scalars().all() # Get all results
    return items

# Read a Single Item by ID
@app.get("/items/{item_id}", response_model=ItemInDB)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).filter(Item.id == item_id))
    item = result.scalars().first() # Get the first result
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Update an Item
@app.put("/items/{item_id}", response_model=ItemInDB)
async def update_item(item_id: int, item: ItemUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).filter(Item.id == item_id))
    db_item = result.scalars().first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    item_data = item.dict(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)

    await db.commit()
    await db.refresh(db_item)
    return db_item

# Delete an Item
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).filter(Item.id == item_id))
    db_item = result.scalars().first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(db_item)
    await db.commit()
    return {"message": "Item deleted successfully"} 