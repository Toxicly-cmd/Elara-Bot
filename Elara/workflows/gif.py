from __future__ import annotations
import requests
import json
import random

from Elara.config.config import urls

def get_gif(name:str,limit:int=10):
    base_url = urls.gif_api_base
    params = {
        "q":name,
        "key":urls.gif_api_key,
        "limit":limit
    }
    response = requests.get(base_url,params=params)
    if response.status_code != 200:
        return None
    data = response.json()    
    results = data.get('results',[])
    selected_gif = random.choice(results) if results else None
    media_list = selected_gif.get('media', [])
    if not media_list:
        # Fallback for Tenor V2 structure
        media_formats = selected_gif.get('media_formats', {})
        if media_formats:
            return media_formats.get('gif', {}).get('url')
        return None
    return media_list[0].get('gif', {}).get('url', None)
