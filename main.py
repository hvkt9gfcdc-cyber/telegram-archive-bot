import os
import sqlite3
import telebot

TOKEN = os.environ[“BOT_TOKEN”]
bot = telebot.TeleBot(TOKEN)
db = sqlite3.connect(“archive.db”, check_same_thread=False)

db.execute(”””
CREATE TABLE IF NOT EXISTS messages (
chat_id INTEGER,
message_id INTEGER,
user_id INTEGER,
text TEXT
)
“””)
db.commit()

@bot.message_handler(commands=[“start”])
def start(message):
bot.reply_to(
message,
“Бот запущен! Я буду архивировать доступные мне текстовые сообщения.”
)

@bot.message_handler(content_types=[“text”])
def save_message(message):
db.execute(
“INSERT INTO messages VALUES (?, ?, ?, ?)”,
(
message.chat.id,
message.message_id,
message.from_user.id if message.from_user else 0,
message.text
)
)
db.commit()

@bot.message_handler(commands=[“archive”])
def archive(message):
rows = db.execute(
“SELECT text FROM messages WHERE chat_id = ? ORDER BY rowid DESC LIMIT 10”,
(message.chat.id,)
).fetchall()

if not rows:
    bot.reply_to(message, "Архив пока пуст.")
    return
result = "\n\n".join(row[0] for row in rows)
bot.reply_to(message, result[:4000])

bot.infinity_polling()
