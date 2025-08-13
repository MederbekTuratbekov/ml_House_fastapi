from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List
from fastapi_house.db.database import get_db
from fastapi_house.db.models import Property
from fastapi_house.db.schema import PropertySchema, PropertyCreateSchema


property_router = APIRouter(prefix='/property', tags=['Property'])

@property_router.post('/', response_model=PropertyCreateSchema)
async def property_create(property:PropertyCreateSchema, db:Session=Depends(get_db)):
    db_property = Property(**property.dict())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

@property_router.get('/', response_model=List[PropertySchema])
async def property_list(db:Session=Depends(get_db)):
    return db.query(Property).all()

@property_router.get('/{property_it}', response_model=PropertySchema)
async def property_detail(property_id:int, db:Session=Depends(get_db)):
    db_property = db.query(Property).filter(Property.id==property_id).first()
    if db_property is None:
        raise HTTPException(status_code=404, detail='Property Not Found')
    return db_property

@property_router.post('/{property_id}', response_model=dict)
async def property_update(property_id:int, property:PropertyCreateSchema, db:Session=Depends(get_db)):
    db_property = db.query(Property).filter(Property.id==property_id).first()
    if db_property is None:
        raise HTTPException(status_code=404, detail='Property Not Found')
    for property_key, property_value in property.dict().items():
        setattr(db_property, property_key, property_value)
    db.commit()
    db.refresh(db_property)
    return {'message':'Update'}

@property_router.delete('/{property_id}', response_model=dict)
async def property_delete(property_id:int, db:Session=Depends(get_db)):
    db_property = db.query(Property).filter(Property.id==property_id).first()
    if db_property is None:
        raise HTTPException(status_code=404, detail='Property Not Found')
    db.delete(db_property)
    db.commit()
    return {'message':'Deleted'}
