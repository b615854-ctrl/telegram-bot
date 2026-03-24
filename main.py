import threading
from flask import Flask
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
from datetime import datetime, timedelta

# ========== ВЕБ-СЕРВЕР ДЛЯ RENDER (чтобы не засыпал) ==========
app = Flask(__name__)

@app.route('/')
def health():
    return "✅ Бот работает", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()
# ==============================================================

# ========== НАСТРОЙКИ БОТА ==========
TOKEN = '8675191350:AAHF-BTAgPWDY4LQjH0udpOzeNT7f-P-Azw'  # ⚠️ ВСТАВЬ СВОЙ ТОКЕН
ADMIN_GROUP_ID = -5172375951     # ID твоей группы

bot = telebot.TeleBot(TOKEN)

# Защита от спама (1 сообщение в 5 секунд)
user_last_message = {}

def can_send_message(user_id):
    now = datetime.now()
    if user_id in user_last_message:
        if now - user_last_message[user_id] < timedelta(seconds=5):
            return False
    user_last_message[user_id] = now
    return True
# ===================================

@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    bot.reply_to(message, f"👋 Привет, {user_name}!\n\nЯ бот-посредник. Все сообщения будут переданы администратору.")
    bot.send_message(ADMIN_GROUP_ID, f"🆕 Новый пользователь: {user_name} (ID: {message.from_user.id})")

@bot.message_handler(func=lambda m: m.chat.type == 'private')
def forward(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    if not can_send_message(user_id):
        bot.reply_to(message, "⏳ Слишком часто! Подождите 5 секунд.")
        return
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✏️ Ответить", callback_data=f"reply_{user_id}"))
    
    bot.send_message(
        ADMIN_GROUP_ID,
        f"📨 **От {user_name}** (ID: `{user_id}`):\n\n{message.text}",
        reply_markup=markup,
        parse_mode='Markdown'
    )
    bot.reply_to(message, "✅ Сообщение отправлено администратору!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def reply_button(call):
    user_id = call.data.split('_')[1]
    bot.answer_callback_query(call.id, "✍️ Введите текст ответа...")
    msg = bot.send_message(ADMIN_GROUP_ID, f"Введите ответ для пользователя ID `{user_id}`:", parse_mode='Markdown')
    bot.register_next_step_handler(msg, send_reply, user_id)

def send_reply(message, user_id):
    try:
        bot.send_message(int(user_id), f"📩 **Ответ от администратора:**\n\n{message.text}", parse_mode='Markdown')
        bot.send_message(ADMIN_GROUP_ID, f"✅ **Ответ отправлен** пользователю `{user_id}`")
    except Exception as e:
        bot.send_message(ADMIN_GROUP_ID, f"❌ **Ошибка:** {str(e)}")

print("🤖 БОТ-ПОСРЕДНИК ЗАПУЩЕН!")
print(f"👥 Группа админа: {ADMIN_GROUP_ID}")

while True:
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")
        time.sleep(15)
