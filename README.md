# Telethon Backuper

A Python application for backing up Telegram data using Telethon.

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your Telegram API credentials
   - Get your API_ID and API_HASH from https://my.telegram.org/apps

5. **Run the application:**
   ```bash
   python main.py
   ```

## Configuration

Edit the `.env` file with your settings:
- `API_ID`: Your Telegram API ID
- `API_HASH`: Your Telegram API Hash
- `PHONE_NUMBER`: Your phone number (with country code)
- `SESSION_NAME`: Name for the session file
- `BACKUP_DIR`: Directory where backups will be stored

## Requirements

- Python 3.7+
- Telegram API credentials

## License

MIT

