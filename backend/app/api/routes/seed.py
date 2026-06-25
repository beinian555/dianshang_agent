from fastapi import APIRouter, Depends

from app.repositories.factory import get_store
from app.repositories.base import StoreBase

router = APIRouter(tags=["seed"])


@router.post("/seed/beauty")
async def seed_beauty(store: StoreBase = Depends(get_store)):
    return await store.seed_beauty_data()
