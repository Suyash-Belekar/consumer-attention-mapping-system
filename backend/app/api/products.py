from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user,require_roles
from app.models.database_models import CameraModel,ProductAttentionModel,ProductMappingModel,ProductModel,ShelfModel,StoreModel,StoreZoneModel
from app.schemas.management import ProductCreate,ProductMappingCreate,ProductMappingResponse,ProductMetricsUpdate,ProductResponse,ProductScoreResponse,ProductUpdate
from app.services.product_scoring import build_store_references,calculate_attractiveness,recommendations
router=APIRouter(prefix="/api/products",tags=["Products & Product Mapping"])
def compute_bbox(polygon):
    xs,ys=zip(*polygon); return {"x_min":min(xs),"y_min":min(ys),"x_max":max(xs),"y_max":max(ys)}
async def get_product(db,product_id):
    obj=await db.get(ProductModel,product_id)
    if obj is None or not obj.is_active: raise HTTPException(404,"Product not found.")
    return obj
async def _validate_placement(db,payload):
    store=await db.get(StoreModel,payload.store_id)
    if store is None: raise HTTPException(404,"Store not found.")
    if getattr(payload,"zone_id",None):
        zone=await db.get(StoreZoneModel,payload.zone_id)
        if zone is None or zone.store_id!=payload.store_id: raise HTTPException(400,"Zone does not belong to the selected store.")
    if getattr(payload,"shelf_id",None):
        shelf=await db.get(ShelfModel,payload.shelf_id)
        if shelf is None or shelf.store_id!=payload.store_id: raise HTTPException(400,"Shelf does not belong to the selected store.")
    if getattr(payload,"camera_id",None):
        camera=await db.get(CameraModel,payload.camera_id)
        if camera is None or camera.store_id!=payload.store_id: raise HTTPException(400,"Camera does not belong to the selected store.")
@router.post("",response_model=ProductResponse,status_code=201,dependencies=[Depends(require_roles("SuperAdmin","StoreManager"))])
async def create_product(payload:ProductCreate,db:AsyncSession=Depends(get_db)):
    await _validate_placement(db,payload); obj=ProductModel(**payload.model_dump(exclude={"metadata"}),metadata_json=payload.metadata); db.add(obj); await db.commit(); await db.refresh(obj); return obj
@router.get("",response_model=list[ProductResponse],dependencies=[Depends(get_current_user)])
async def list_products(store_id:UUID|None=None,shelf_id:UUID|None=None,camera_id:str|None=None,db:AsyncSession=Depends(get_db)):
    stmt=select(ProductModel).where(ProductModel.is_active.is_(True)).order_by(ProductModel.name.asc())
    if store_id: stmt=stmt.where(ProductModel.store_id==store_id)
    if shelf_id: stmt=stmt.where(ProductModel.shelf_id==shelf_id)
    if camera_id: stmt=stmt.where(ProductModel.camera_id==camera_id)
    return (await db.execute(stmt)).scalars().all()
@router.post("/mappings",response_model=ProductMappingResponse,status_code=201,dependencies=[Depends(require_roles("SuperAdmin","StoreManager"))])
async def create_mapping(payload:ProductMappingCreate,db:AsyncSession=Depends(get_db)):
    product=await get_product(db,payload.product_id)
    if product.store_id!=payload.store_id: raise HTTPException(400,"Product and mapping store must match.")
    await _validate_placement(db,payload)
    obj=await db.scalar(select(ProductMappingModel).where(ProductMappingModel.product_id==payload.product_id,ProductMappingModel.shelf_id==payload.shelf_id,ProductMappingModel.camera_id==payload.camera_id,ProductMappingModel.is_active.is_(True)))
    if obj is None: obj=ProductMappingModel(**payload.model_dump()); db.add(obj)
    obj.roi_polygon=payload.roi_polygon; obj.bbox=compute_bbox(payload.roi_polygon); obj.tier=payload.tier; obj.is_active=True
    product.shelf_id=payload.shelf_id
    product.zone_id=product.zone_id
    if payload.camera_id: product.camera_id=payload.camera_id
    await db.commit(); await db.refresh(obj); return obj
@router.get("/mappings",response_model=list[ProductMappingResponse],dependencies=[Depends(get_current_user)])
async def list_mappings(store_id:UUID|None=None,shelf_id:UUID|None=None,product_id:UUID|None=None,camera_id:str|None=None,db:AsyncSession=Depends(get_db)):
    stmt=select(ProductMappingModel).where(ProductMappingModel.is_active.is_(True)).order_by(ProductMappingModel.created_at.desc())
    for field,value in ((ProductMappingModel.store_id,store_id),(ProductMappingModel.shelf_id,shelf_id),(ProductMappingModel.product_id,product_id),(ProductMappingModel.camera_id,camera_id)):
        if value is not None: stmt=stmt.where(field==value)
    return (await db.execute(stmt)).scalars().all()
@router.get("/scores",dependencies=[Depends(get_current_user)])
async def product_scores(store_id:UUID,db:AsyncSession=Depends(get_db)):
    products=(await db.execute(select(ProductModel).where(ProductModel.store_id==store_id,ProductModel.is_active.is_(True)).order_by(ProductModel.name))).scalars().all()
    metrics_rows=(await db.execute(select(ProductAttentionModel).where(ProductAttentionModel.store_id==store_id))).scalars().all(); refs=build_store_references(metrics_rows); by={m.product_id:m for m in metrics_rows}; result=[]
    for product in products:
        metrics=by.get(product.id)
        if metrics is None: continue
        score,breakdown=calculate_attractiveness(metrics,refs)
        result.append({"product_id":product.id,"product_name":product.name,"attractiveness_score":score,"metrics_breakdown":breakdown,"recommendations":recommendations(metrics,breakdown)})
    return sorted(result,key=lambda x:x["attractiveness_score"],reverse=True)
@router.get("/{product_id}/mapping",response_model=ProductMappingResponse,dependencies=[Depends(get_current_user)])
async def get_mapping(product_id:UUID,camera_id:str|None=None,db:AsyncSession=Depends(get_db)):
    stmt=select(ProductMappingModel).where(ProductMappingModel.product_id==product_id,ProductMappingModel.is_active.is_(True)).order_by(ProductMappingModel.created_at.desc())
    if camera_id: stmt=stmt.where(ProductMappingModel.camera_id==camera_id)
    obj=(await db.execute(stmt)).scalars().first()
    if obj is None: raise HTTPException(404,"Product mapping not found.")
    return obj
@router.put("/{product_id}/mapping",response_model=ProductMappingResponse,dependencies=[Depends(require_roles("SuperAdmin","StoreManager"))])
async def update_mapping(product_id:UUID,payload:ProductMappingCreate,db:AsyncSession=Depends(get_db)):
    product=await get_product(db,product_id)
    if payload.product_id != product_id:
        raise HTTPException(400,"Payload product_id must match the URL product_id.")
    if payload.store_id != product.store_id:
        raise HTTPException(400,"Product and mapping store must match.")
    await _validate_placement(db,payload)
    stmt=select(ProductMappingModel).where(ProductMappingModel.product_id==product_id,ProductMappingModel.is_active.is_(True))
    if payload.camera_id: stmt=stmt.where(ProductMappingModel.camera_id==payload.camera_id)
    obj=(await db.execute(stmt.order_by(ProductMappingModel.created_at.desc()))).scalars().first()
    if obj is None: raise HTTPException(404,"Product mapping not found for this camera.")
    data = payload.model_dump(exclude={"product_id"})
    for key, value in data.items():
        setattr(obj, key, value)
    obj.bbox=compute_bbox(payload.roi_polygon); product.shelf_id=payload.shelf_id
    product.zone_id=product.zone_id
    if payload.camera_id: product.camera_id=payload.camera_id
    await db.commit(); await db.refresh(obj); return obj
@router.delete("/{product_id}/mapping",status_code=204,dependencies=[Depends(require_roles("SuperAdmin","StoreManager"))])
async def delete_mapping(product_id:UUID,camera_id:str|None=None,db:AsyncSession=Depends(get_db)):
    stmt=select(ProductMappingModel).where(ProductMappingModel.product_id==product_id,ProductMappingModel.is_active.is_(True))
    if camera_id: stmt=stmt.where(ProductMappingModel.camera_id==camera_id)
    obj=(await db.execute(stmt.order_by(ProductMappingModel.created_at.desc()))).scalars().first()
    if obj is None: raise HTTPException(404,"Product mapping not found.")
    obj.is_active=False; await db.commit()
@router.put("/{product_id}/metrics",response_model=ProductScoreResponse,dependencies=[Depends(require_roles("SuperAdmin","StoreManager"))])
async def update_metrics(product_id:UUID,payload:ProductMetricsUpdate,db:AsyncSession=Depends(get_db)):
    product=await get_product(db,product_id); metrics=await db.scalar(select(ProductAttentionModel).where(ProductAttentionModel.product_id==product_id))
    if metrics is None: metrics=ProductAttentionModel(product_id=product_id,store_id=product.store_id,shelf_id=product.shelf_id,camera_id=product.camera_id); db.add(metrics)
    for key,value in payload.model_dump().items(): setattr(metrics,key,value)
    await db.flush(); all_metrics=(await db.execute(select(ProductAttentionModel).where(ProductAttentionModel.store_id==product.store_id))).scalars().all(); score,breakdown=calculate_attractiveness(metrics,build_store_references(all_metrics)); await db.commit()
    return ProductScoreResponse(product_id=product_id,product_name=product.name,attractiveness_score=score,metrics_breakdown=breakdown,recommendations=recommendations(metrics,breakdown))
@router.get("/{product_id}/attractiveness-analysis",response_model=ProductScoreResponse,dependencies=[Depends(get_current_user)])
async def attractiveness(product_id:UUID,db:AsyncSession=Depends(get_db)):
    product=await get_product(db,product_id); metrics=await db.scalar(select(ProductAttentionModel).where(ProductAttentionModel.product_id==product_id))
    if metrics is None: raise HTTPException(404,"Product metrics not found.")
    all_metrics=(await db.execute(select(ProductAttentionModel).where(ProductAttentionModel.store_id==product.store_id))).scalars().all(); score,breakdown=calculate_attractiveness(metrics,build_store_references(all_metrics))
    return ProductScoreResponse(product_id=product_id,product_name=product.name,attractiveness_score=score,metrics_breakdown=breakdown,recommendations=recommendations(metrics,breakdown))
@router.get("/{product_id}",response_model=ProductResponse,dependencies=[Depends(get_current_user)])
async def product_detail(product_id:UUID,db:AsyncSession=Depends(get_db)): return await get_product(db,product_id)
@router.put("/{product_id}",response_model=ProductResponse,dependencies=[Depends(require_roles("SuperAdmin","StoreManager"))])
async def update_product(product_id:UUID,payload:ProductUpdate,db:AsyncSession=Depends(get_db)):
    obj=await get_product(db,product_id); data=payload.model_dump(exclude_unset=True)
    if "metadata" in data: obj.metadata_json=data.pop("metadata") or {}
    for key,value in data.items(): setattr(obj,key,value)
    await db.commit(); await db.refresh(obj); return obj
@router.delete("/{product_id}",status_code=204,dependencies=[Depends(require_roles("SuperAdmin","StoreManager"))])
async def delete_product(product_id:UUID,db:AsyncSession=Depends(get_db)):
    obj=await get_product(db,product_id); obj.is_active=False; await db.commit()
