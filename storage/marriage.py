from __future__ import annotations
from storage.engine import CollectionStore, NOW

CollectionName = 'marriage'

_store = CollectionStore(
    name=CollectionName,
    defaults={'timestamp': NOW},
    unique_sets=[['user1_id'], ['user2_id']],
    datetime_fields=set(['timestamp']),
)

async def create_table():
    return await _store.prepare()

async def insert(user1_id: int, user2_id: int):
    return await _store.insert(locals())

async def get_marriage(user_id: int):
    return await _store.get({"$or": [{"user1_id": user_id}, {"user2_id": user_id}]})

async def marry(user1_id: int, user2_id: int):
    return await _store.insert(locals())

async def divorce(user_id: int):
    collection = await _store._collection()
    await collection.delete_many({"$or": [{"user1_id": user_id}, {"user2_id": user_id}]})
    return True
