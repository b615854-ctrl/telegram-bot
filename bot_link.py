import threading
from flask import Flask
import os
import telebot
import time

# ========== ВЕБ-СЕРВЕР ДЛЯ RENDER (ОБЯЗАТЕЛЬНО) ==========
app = Flask(__name__)

@app.route('/')
def health():
    return "✅ Бот со ссылкой работает", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()
# ========================================================

# ========== НАСТРОЙКИ БОТА ==========
TOKEN = '8681961770:AAFuVjp8ynlIZyJ4iU6uaJbbIljyAY61hLg'  # ⚠️ ВСТАВЬ СВОЙ ТОКЕН
CHANNEL_LINK = 'https://t.me/+Qp11MrinOD9iMjli'

bot = telebot.TeleBot(TOKEN)
# ===================================

@bot.message_handler(commands=['start'])
def send_link(message):
    user_name = message.from_user.first_name
    bot.reply_to(
        message,
        f"👋 Привет, {user_name}!\n\n"
        f"🔗 Вот ссылка на наш закрытый канал:\n"
        f"{CHANNEL_LINK}\n\n"
        f"Нажми, чтобы присоединиться ✅"
    )

@bot.message_handler(func=lambda m: True)
def help_message(message):
    bot.reply_to(message, "📢 Отправьте /start, чтобы получить ссылку на канал")

print("🤖 БОТ-ССЫЛКА ЗАПУЩЕН!")
print(f"🔗 Канал: {CHANNEL_LINK}")

while True:
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")
        time.sleep(15)
