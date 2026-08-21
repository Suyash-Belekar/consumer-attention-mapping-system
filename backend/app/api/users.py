from __future__ import annotations
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import get_current_user,get_password_hash,require_roles
from app.models.database_models import RoleModel,UserModel
router=APIRouter(prefix="/api/users",tags=["User Management"])
class UserCreate(BaseModel): email:EmailStr; password:str; full_name:str|None=None; role_id:int
class UserUpdate(BaseModel): full_name:str|None=None; role_id:int|None=None; is_active:bool|None=None; password:str|None=None
@router.get("/me")
async def me(current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    user=await db.scalar(select(UserModel).options(selectinload(UserModel.role)).where(UserModel.email==current_user.get("sub")))
    return {"id":user.id,"email":user.email,"full_name":user.full_name,"role":user.role.role_name,"is_active":user.is_active} if user else {"email":current_user.get("sub"),"role":current_user.get("role")}
@router.get("",dependencies=[Depends(require_roles("SuperAdmin"))])
async def list_users(db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(UserModel).options(selectinload(UserModel.role)).order_by(UserModel.email))).scalars().all(); return [{"id":u.id,"email":u.email,"full_name":u.full_name,"role":u.role.role_name,"role_id":u.role_id,"is_active":u.is_active} for u in rows]
@router.post("",status_code=201,dependencies=[Depends(require_roles("SuperAdmin"))])
async def create_user(payload:UserCreate,db:AsyncSession=Depends(get_db)):
    if await db.scalar(select(UserModel).where(UserModel.email==payload.email)): raise HTTPException(409,"Email already registered.")
    if await db.get(RoleModel,payload.role_id) is None: raise HTTPException(400,"Invalid role.")
    user=UserModel(email=payload.email,password_hash=get_password_hash(payload.password),full_name=payload.full_name,role_id=payload.role_id); db.add(user); await db.commit(); await db.refresh(user); return {"id":user.id,"email":user.email,"full_name":user.full_name,"role_id":user.role_id,"is_active":user.is_active}
@router.put("/{user_id}",dependencies=[Depends(require_roles("SuperAdmin"))])
async def update_user(user_id:int,payload:UserUpdate,db:AsyncSession=Depends(get_db)):
    user=await db.get(UserModel,user_id)
    if user is None: raise HTTPException(404,"User not found.")
    data=payload.model_dump(exclude_unset=True)
    if "password" in data: user.password_hash=get_password_hash(data.pop("password"))
    for key,value in data.items(): setattr(user,key,value)
    await db.commit(); await db.refresh(user); return {"id":user.id,"email":user.email,"full_name":user.full_name,"role_id":user.role_id,"is_active":user.is_active}
