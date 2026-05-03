import os
import re

files_to_fix = [
    ("Elara/src/commands/backup.py", "Backup"),
    ("Elara/src/commands/ticket.py", "Ticket"),
    ("Elara/src/commands/moderation.py", "Moderation"),
    ("Elara/src/commands/security.py", "Security"),
    ("Elara/src/commands/more.py", "More"),
    ("Elara/src/commands/welcomer.py", "Welcomer"),
    ("Elara/src/commands/giveaway.py", "Giveaway"),
    ("Elara/src/commands/automod.py", "Automod"),
    ("Elara/src/events/on_message_delete.py", "on_message_delete"),
    ("Elara/src/events/on_invite_delete.py", "on_invite_delete"),
    ("Elara/src/events/on_webhooks_update.py", "on_webhooks_update"),
    ("Elara/src/events/on_member_join.py", "on_member_join"),
    ("Elara/src/events/on_member_update.py", "on_member_update"),
    ("Elara/src/events/on_guild_update.py", "on_guild_update"),
    ("Elara/src/events/on_message_edit.py", "on_message_edit"),
    ("Elara/src/events/on_voice_state_update.py", "on_voice_state_update"),
    ("Elara/src/events/on_invite_create.py", "on_invite_create"),
    ("Elara/src/events/on_guild_remove.py", "on_guild_remove"),
    ("Elara/src/events/on_member_remove.py", "on_member_remove"),
    ("Elara/src/events/on_guild_emojis_update.py", "on_guild_emojis_update"),
    ("Elara/src/events/ready.py", "ready"),
    ("Elara/src/events/on_guild_channel_update.py", "on_guild_channel_update"),
    ("Elara/src/events/wavelink.py", "Wavelink"),
    ("Elara/src/events/on_guild_channel_delete.py", "on_guild_channel_delete"),
    ("Elara/src/events/on_guild_role_create.py", "on_guild_role_create"),
    ("Elara/src/events/on_command.py", "on_command"),
    ("Elara/src/events/on_guild_channel_create.py", "on_guild_channel_create"),
    ("Elara/src/events/on_guild_role_delete.py", "on_guild_role_delete"),
    ("Elara/src/events/on_guild_join.py", "on_guild_join"),
    ("Elara/src/events/on_guild_role_update.py", "on_guild_role_update"),
    ("Elara/src/events/on_member_unban.py", "on_member_unban"),
]

for filepath, classname in files_to_fix:
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}: File not found")
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    if 'async def setup' in content:
        print(f"Skipping {filepath}: Setup function already exists")
        continue
    
    setup_code = f"\n\nasync def setup(bot):\n    await bot.add_cog({classname}(bot))\n"
    
    with open(filepath, 'a') as f:
        f.write(setup_code)
    print(f"Fixed {filepath} by adding setup function for {classname}")
