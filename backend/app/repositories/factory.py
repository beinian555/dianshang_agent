"""Store factory: returns MemoryStore or PostgresStore based on STORE_BACKEND env var."""

import os

from app.repositories.base import StoreBase
from app.repositories.memory_store import memory_store


def get_store() -> StoreBase:
    backend = os.getenv("STORE_BACKEND", "memory").strip().lower()
    if backend == "postgres":
        from app.repositories.postgres_store import PostgresStore
        return PostgresStore()
    return memory_store
