"""
Configuration module for Telethon Backuper
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""
    
    # Telegram API Configuration
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER')
    
    # Session Configuration
    SESSION_NAME = os.getenv('SESSION_NAME', 'telethon_backup_session')
    
    # Backup Settings
    BACKUP_DIR = os.getenv('BACKUP_DIR', './backups')
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        missing = []
        
        if not cls.API_ID:
            missing.append('API_ID')
        if not cls.API_HASH:
            missing.append('API_HASH')
        if not cls.PHONE_NUMBER:
            missing.append('PHONE_NUMBER')
        
        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}\n"
                "Please check your .env file."
            )
        
        return True

