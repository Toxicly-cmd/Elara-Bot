from __future__ import annotations
from storage.engine import CollectionStore, NOW

CollectionName = 'chat_bans'

_store = CollectionStore(
    name=CollectionName,
    defaults={'created_at': NOW},
    unique_sets=[['guild_id', 'user_id']],
    json_fields=set([]),
    datetime_fields=set(['created_at']),
    sequence_fields={},
    update_cache=('chat_bans_cache', ['guild_id', 'user_id']),
    delete_cache=('chat_bans_cache', ['guild_id', 'user_id']),
)

async def create_table():
    return await _store.prepare()

async def insert(
    id:int=None,
    guild_id:int=None,
    user_id:int=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(
    id:int,
    guild_id:int=None,
    user_id:int=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(
    id:int=None,
    guild_id:int=None,
    user_id:int=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(
    id:int=None,
    guild_id:int=None,
    user_id:int=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(
    id:int=None,
    guild_id:int=None,
    user_id:int=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()
