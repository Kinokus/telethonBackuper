import os
from dotenv import load_dotenv
from telethon import TelegramClient, events

# Завантажуємо змінні середовища з .env файлу
load_dotenv()

# Отримай ці значення на https://my.telegram.org → API development tools
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Ім'я файлу для збереження сесії (логіну)
client = TelegramClient('userbot', api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    print(event.to_dict()['message'])
    # sender = await event.get_sender()
    # print(f"📩 Нове повідомлення від {sender.first_name}: {event.raw_text}")

    # Приклад: якщо хтось напише "ping" → відповісти "pong"
    # if event.raw_text.lower() == "ping":
        # await event.reply("pong")

async def main():
    print("✅ Userbot запущено. Очікування повідомлень...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
