from __future__ import annotations
import wavelink
import asyncio

import os
from Elara.console.logging import logger



running = False
async def on_node(bot):
    global running
    while not bot.is_ready():
        # logger.info("Waiting for bot to be ready to connect to Lavalink")
        await asyncio.sleep(1)
    if running:
        await wavelink.Pool.reconnect()
        return logger.info("Reconnected to Lavalink nodes")
    running = True
    
    # Pull premium credentials from environment variables
    lava_host = os.getenv("LAVALINK_HOST", "178.156.172.214")
    lava_port = os.getenv("LAVALINK_PORT", "4040")
    lava_pass = os.getenv("LAVALINK_PASSWORD", "smoothbatter")
    lava_secure = os.getenv("LAVALINK_SECURE", "False").lower() == "true"
    
    protocol = "https" if lava_secure else "http"
    uri = f"{protocol}://{lava_host}:{lava_port}/"
    
    nodes = [
        wavelink.Node(uri=uri, password=lava_pass, retries=5),
        wavelink.Node(uri="https://lava-v4.ajieblogs.eu.org:443/", password="https://dsc.gg/ajidevserver", retries=3)
    ]
    
    try:
        await wavelink.Pool.connect(
            nodes=nodes,
            client=bot
        )
        logger.success(f"Connected to Lavalink with {len(nodes)} nodes")
    except Exception as e:
        logger.error(f"Failed to connect to Lavalink Pool: {e}")
