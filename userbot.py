import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
import json
from datetime import datetime
import psycopg2
import csv
import io


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
    """Handle /chats command to export groups as CSV"""
    try:
        await event.reply("📊 Generating groups CSV...")
        
        # Get all dialogs (chats)
        dialogs = await client.get_dialogs()
        await event.reply(f"📊 Found {len(dialogs)} groups")
        # Connect to database to get message counts
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER") or "postgres",
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()
        
        # Create CSV in memory
        output = io.StringIO()
        csv_writer = csv.writer(output)
        
        # Write header
        csv_writer.writerow(['id', 'username', 'name', 'message_count'])
        
        group_count = 0
        # Filter for groups only (Channel, Chat, Megagroup)
        for dialog in dialogs:
            print(group_count, dialog.entity.id)
            chat = dialog.entity
            # chat_type = chat.__class__.__name__
            # Filter for groups/channels (not User, not bot)
            # if chat_type in ['Channel', 'Chat']:
            chat_id = chat.id
            username = getattr(chat, 'username', None) or ''
            
            # Get name: title for groups, or firstname + lastname for users
            if hasattr(chat, 'title') and chat.title:
                name = chat.title
            else:
                first_name = getattr(chat, 'first_name', '') or ''
                last_name = getattr(chat, 'last_name', '') or ''
                name = f"{first_name} {last_name}".strip()
            
            # Get message count from database
            cur.execute("""
                SELECT COUNT(*) FROM telegram.raw_messages 
                WHERE chat_id = %s
            """, (chat_id,))
            result = cur.fetchone()
            message_count = result[0] if result else 0
            
            # Write row to CSV
            csv_writer.writerow([chat_id, username, name, message_count])
            group_count += 1
        
        cur.close()
        conn.close()
        
        # Get CSV content
        csv_content = output.getvalue()
        output.close()
        
        # Send CSV as file
        csv_bytes = io.BytesIO(csv_content.encode('utf-8'))
        csv_bytes.name = 'groups.csv'
        await event.reply(
            f"✅ Found {group_count} groups",
            file=csv_bytes
        )
        
    except Exception as e:
        await event.reply(f"❌ Error generating CSV: {str(e)}")
        print(f"Error in list_chats_command: {e}")
        import traceback
        traceback.print_exc()

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
        if sender:
            sender_json = json.dumps(sender.to_dict(), cls=DateTimeEncoder)
            username = getattr(sender, 'username', None)
            first_name = getattr(sender, 'first_name', None)
            last_name = getattr(sender, 'last_name', None)
            title = getattr(sender, 'title', None)
            is_bot = getattr(sender, 'bot', False)
        else:
            sender_json = None
            username = None
            first_name = None
            last_name = None
            title = None
            is_bot = False
        
        # chat and user same structure so we can use the same function to insert both
        if chat:
            raw_chat_json = json.dumps(chat.to_dict(), cls=DateTimeEncoder)
        else:
            raw_chat_json = None
        
        if chat_id is not None:
            cur.execute("""
                INSERT INTO telegram.users (user_id, json_data, title, first_name, last_name)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING
            """, (chat_id, raw_chat_json, chat_title, chat_first_name, chat_last_name))

        if sender_id is not None:
            cur.execute("""
                INSERT INTO telegram.users (user_id, username, first_name, last_name, title, is_bot, json_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING
            """, (sender_id, username, first_name, last_name, title, is_bot, sender_json))
        
        # Now insert the message
        if event.message:
            raw_message_json = json.dumps(event.message.to_dict(), cls=DateTimeEncoder)
            message_id = event.message.id
            date = event.message.date
        else:
            raw_message_json = None
            message_id = None
            date = None

        print(f"Chat ID: {chat_id}, Sender ID: {sender_id}, Message ID: {message_id}, Date: {date}")

        if message_id is not None:
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
