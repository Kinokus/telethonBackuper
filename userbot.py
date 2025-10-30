import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
import json
from datetime import datetime
import psycopg2


# Custom JSON encoder to handle datetime and bytes objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, bytes):
            return obj.hex()  # Convert bytes to hex string
        return super().default(obj)


# Завантажуємо змінні середовища з .env файлу
load_dotenv()

# Отримай ці значення на https://my.telegram.org → API development tools
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Ім'я файлу для збереження сесії (логіну)
client = TelegramClient(
    'userbot_'+os.getenv('USER_PHONE'), 
    api_id, 
    api_hash
    )

# @client.on(events.NewMessage)
# async def handler(event):
#     print(json.dumps(event.message.to_dict(), cls=DateTimeEncoder))
#     print(json.dumps(event.sender.to_dict(), cls=DateTimeEncoder))

@client.on(events.NewMessage(pattern=r'/chats', outgoing=True))
async def list_chats_command(event):
    """Handle /chats command to list all user's chats"""
    try:
        # React to the command message
        # await event.message.react('👍')
        
        # Get all dialogs (chats)
        dialogs = await client.get_dialogs()
        print(dialogs)
        # Build the chat list
        chat_list = []
        for dialog in dialogs:
            chat = dialog.entity
            chat_info = {
                'id': chat.id,
                'name': getattr(chat, 'title', None) or getattr(chat, 'first_name', None) or 'Unknown',
                'type': chat.__class__.__name__,
                'unread': dialog.unread_count
            }
            chat_list.append(f"• {chat_info['name']} (ID: {chat_info['id']}, Type: {chat_info['type']}, Unread: {chat_info['unread']})")
        
        # Send the list as a reply
        response = f"📋 **Your Chats ({len(chat_list)} total):**\n\n" + "\n".join(chat_list)
        await event.reply(response)
        
    except Exception as e:
        await event.reply(f"❌ Error listing chats: {str(e)}")
        print(f"Error in list_chats_command: {e}")

@client.on(events.NewMessage)
async def save_raw_message(event):
    # Connect to the database
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER") or "postgres",
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    try:
        chat = await event.get_chat()
        sender = await event.get_sender()
        chat_id = chat.id if chat else None
        sender_id = sender.id if sender else None
        
        chat_title = None
        chat_first_name = None
        chat_last_name = None
        
        try:
            chat_title = chat.title
        except:
            pass
        
        try:
            chat_first_name = chat.first_name
        except:
            pass
        
        
        try:
            chat_last_name = chat.last_name
        except:
            pass
        cur = conn.cursor()
        
        # Insert or update user if not exists
        sender_json = json.dumps(sender.to_dict(), cls=DateTimeEncoder)
        username = getattr(sender, 'username', None)
        first_name = getattr(sender, 'first_name', None)
        last_name = getattr(sender, 'last_name', None)
        title = getattr(sender, 'title', None)
        is_bot = getattr(sender, 'bot', False)
        
        # chat and user same structure so we can use the same function to insert both
        raw_chat_json = json.dumps(chat.to_dict(), cls=DateTimeEncoder)
        cur.execute("""
            INSERT INTO telegram.users (user_id, json_data, title, first_name, last_name)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (chat_id, raw_chat_json, chat_title, chat_first_name, chat_last_name))


        cur.execute("""
            INSERT INTO telegram.users (user_id, username, first_name, last_name, title, is_bot, json_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (sender_id, username, first_name, last_name, title, is_bot, sender_json))
        
        # Now insert the message
        raw_message_json = json.dumps(event.message.to_dict(), cls=DateTimeEncoder)
        message_id = event.message.id if event.message else None
        date = event.message.date if event.message else None

        print(f"Chat ID: {chat_id}, Sender ID: {sender_id}, Message ID: {message_id}, Date: {date}")

        cur.execute("""
            INSERT INTO telegram.raw_messages (chat_id, sender_id, message_id, json_data, received_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (chat_id, sender_id, message_id, raw_message_json, date))
        conn.commit()
        cur.close()
    except Exception as e:
        print("DB error while saving raw message:", e)
    finally:
        conn.close()

async def main():
    print("✅ Userbot запущено. Очікування повідомлень...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
