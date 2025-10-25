#!/usr/bin/env python3
"""
Telethon Backuper - Main Application
"""

import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Load environment variables
load_dotenv()

# Configuration from environment
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
SESSION_NAME = os.getenv('SESSION_NAME', 'telethon_backup_session')
BACKUP_DIR = os.getenv('BACKUP_DIR', './backups')


def validate_config():
    """Validate that all required configuration is present."""
    if not API_ID or not API_HASH or not PHONE_NUMBER:
        raise ValueError(
            "Missing required configuration. Please check your .env file.\n"
            "Required: API_ID, API_HASH, PHONE_NUMBER"
        )


async def main():
    """Main application entry point."""
    # Validate configuration
    validate_config()
    
    # Create backup directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Create Telegram client
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    print("Starting Telethon Backuper...")
    
    await client.start(phone=PHONE_NUMBER)
    
    if await client.is_user_authorized():
        print("Successfully connected to Telegram!")
        me = await client.get_me()
        print(f"Logged in as: {me.first_name} (@{me.username})")
        
        # TODO: Implement backup functionality here
        print(f"\nBackup directory: {BACKUP_DIR}")
        print("Ready to perform backups...")
        
    else:
        print("Authorization failed. Please check your credentials.")
    
    await client.disconnect()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

