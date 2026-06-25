"""Backward-compatible re-export shim. Use repositories.factory.get_store() for new code."""

from app.repositories.memory_store import MemoryStore, memory_store

Store = MemoryStore  # backward compat alias
store = memory_store
