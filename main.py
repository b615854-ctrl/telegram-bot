import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import os

TOKEN = '8675191350:AAEXhVU11_i_IFHI-4DPVp1-8SAQk510r7U'
ADMIN_GROUP_ID = int(os.environ.get('ADMIN_GROUP_ID', -5172375951))

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Привет! Я бот-посредник.")
    bot.send_message(ADMIN_GROUP_ID, f"🆕 Новый пользователь: {message.from_user.first_name}")

@bot.message_handler(func=lambda m: m.chat.type == 'private')
def forward(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✏️ Ответить", callback_data=f"reply_{message.from_user.id}"))
    bot.send_message(
        ADMIN_GROUP_ID,
        f"📨 От {message.from_user.first_name}:\n{message.text}",
        reply_markup=markup
    )
    bot.reply_to(message, "✅ Отправлено!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def reply_button(call):
    user_id = call.data.split('_')[1]
    bot.answer_callback_query(call.id, "Введите ответ...")
    msg = bot.send_message(ADMIN_GROUP_ID, f"Введите ответ для {user_id}:")
    bot.register_next_step_handler(msg, send_reply, user_id)

def send_reply(message, user_id):
    try:
        bot.send_message(int(user_id), f"📩 Ответ:\n{message.text}")
        bot.send_message(ADMIN_GROUP_ID, f"✅ Отправлено {user_id}")
    except Exception as e:
        bot.send_message(ADMIN_GROUP_ID, f"❌ Ошибка: {e}")

print("🤖 БОТ ЗАПУЩЕН!")
print(f"Бот: @{bot.get_me().username}")

while True:
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(15)
