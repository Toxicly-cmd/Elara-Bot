from __future__ import annotations
from storage.engine import CollectionStore, NOW, _clean_document

CollectionName = 'member_stats'

_store = CollectionStore(
    name=CollectionName,
    defaults={
        'messages_all_time': 0,
        'messages_weekly': 0,
        'messages_daily': 0,
        'voice_all_time': 0,
        'voice_weekly': 0,
        'voice_daily': 0,
        'voice_muted_all_time': 0,
        'voice_muted_weekly': 0,
        'voice_muted_daily': 0,
        'voice_deafened_all_time': 0,
        'voice_deafened_weekly': 0,
        'voice_deafened_daily': 0,
        'voice_afk_all_time': 0,
        'voice_afk_weekly': 0,
        'voice_afk_daily': 0,
        'invites_total': 0,
        'invites_regular': 0,
        'invites_fake': 0,
        'invites_leaves': 0,
        'invited_by': None,
        'last_update': NOW,
        'created_at': NOW
    },
    unique_sets=[['user_id', 'guild_id']],
    json_fields=set([]),
    datetime_fields=set(['last_update', 'created_at']),
    sequence_fields={},
    update_cache=('member_stats_cache', ['user_id', 'guild_id']),
    delete_cache=('member_stats_cache', ['user_id', 'guild_id']),
)

async def create_table():
    return await _store.prepare()

async def insert(**kwargs):
    return await _store.insert(kwargs)

async def update(**kwargs):
    return await _store.update(kwargs)

async def get(**kwargs):
    return await _store.get(kwargs)

async def gets(**kwargs):
    return await _store.gets(kwargs)

async def delete(**kwargs):
    return await _store.delete(kwargs)

async def get_top(guild_id: int, field: str, limit: int = 10):
    collection = await _store._collection()
    cursor = collection.find({'guild_id': guild_id}).sort(field, -1).limit(limit)
    return [_clean_document(doc, _store.datetime_fields) for doc in await cursor.to_list(length=limit)]

async def increment(user_id: int, guild_id: int, field: str, delta: int = 1):
    return await _store.adjust_field(
        filters={'user_id': user_id, 'guild_id': guild_id},
        field=field,
        delta=delta,
        upsert=True
    )

async def update_member_stats(user_id: int, guild_id: int, **kwargs):
    prepared = _store._build_filters({'user_id': user_id, 'guild_id': guild_id})
    current = await _store.get(prepared)
    if not current:
        await _store.insert(prepared)
        current = await _store.get(prepared)
    
    if current:
        update_data = {'id': current['id']}
        update_data.update(kwargs)
        return await _store.update(update_data)
    return None

async def reset_user_stats(user_id: int, guild_id: int, category: str):
    prepared = _store._build_filters({'user_id': user_id, 'guild_id': guild_id})
    current = await _store.get(prepared)
    if not current:
        return None
    
    fields = {}
    if category == "messages":
        fields = {'messages_all_time': 0, 'messages_weekly': 0, 'messages_daily': 0}
    elif category == "voice":
        fields = {
            'voice_all_time': 0, 'voice_weekly': 0, 'voice_daily': 0,
            'voice_muted_all_time': 0, 'voice_deafened_all_time': 0, 'voice_afk_all_time': 0
        }
    elif category == "invites":
        fields = {'invites_total': 0, 'invites_regular': 0, 'invites_fake': 0, 'invites_leaves': 0}

    if fields:
        update_data = {'id': current['id']}
        update_data.update(fields)
        return await _store.update(update_data)
    return None

async def reset_guild_stats(guild_id: int, category: str):
    collection = await _store._collection()
    fields = {}
    if category == "messages":
        fields = {'messages_all_time': 0, 'messages_weekly': 0, 'messages_daily': 0}
    elif category == "voice":
        fields = {
            'voice_all_time': 0, 'voice_weekly': 0, 'voice_daily': 0,
            'voice_muted_all_time': 0, 'voice_deafened_all_time': 0, 'voice_afk_all_time': 0
        }
    elif category == "invites":
        fields = {'invites_total': 0, 'invites_regular': 0, 'invites_fake': 0, 'invites_leaves': 0}

    if fields:
        await collection.update_many({'guild_id': guild_id}, {'$set': fields})
        return True
    return False

async def reset_daily():
    collection = await _store._collection()
    await collection.update_many({}, {'$set': {
        'messages_daily': 0,
        'voice_daily': 0,
        'voice_muted_daily': 0,
        'voice_deafened_daily': 0,
        'voice_afk_daily': 0
    }})

async def reset_weekly():
    collection = await _store._collection()
    await collection.update_many({}, {'$set': {
        'messages_weekly': 0,
        'voice_weekly': 0,
        'voice_muted_weekly': 0,
        'voice_deafened_weekly': 0,
        'voice_afk_weekly': 0
    }})
