import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
from datetime import datetime, timedelta

# ВСТАВЬТЕ ВАШ НОВЫЙ ТОКЕН
TOKEN = '8675191350:AAHF-BTAgPWDY4LQjH0udpOzeNT7f-P-Azw'
ADMIN_GROUP_ID = -5172375951

bot = telebot.TeleBot(TOKEN)

# Словарь для хранения времени последнего сообщения пользователя
user_last_message = {}

def can_send_message(user_id):
    """Проверяет, можно ли отправить сообщение (не чаще 1 раза в 5 секунд)"""
    now = datetime.now()
    if user_id in user_last_message:
        last_time = user_last_message[user_id]
        if now - last_time < timedelta(seconds=5):
            return False
    user_last_message[user_id] = now
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    bot.reply_to(message, f"👋 Привет, {user_name}!\n\nЯ бот-посредник. Отправляйте сообщения, они будут переданы администратору.\n\n⚠️ Не чаще 1 сообщения в 5 секунд!")
    bot.send_message(ADMIN_GROUP_ID, f"🆕 Новый пользователь: {user_name} (ID: {user_id})")

@bot.message_handler(func=lambda m: m.chat.type == 'private')
def forward(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Проверка на спам
    if not can_send_message(user_id):
        bot.reply_to(message, "⏳ Слишком часто! Подождите 5 секунд перед следующим сообщением.")
        return
    
    # Создаем клавиатуру для ответа
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✏️ Ответить", callback_data=f"reply_{user_id}"))
    
    # Формируем сообщение админу
    admin_msg = f"📨 **От {user_name}** (ID: `{user_id}`):\n\n{message.text}"
    
    try:
        bot.send_message(
            ADMIN_GROUP_ID,
            admin_msg,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.reply_to(message, "✅ Сообщение отправлено администратору!")
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка при отправке. Попробуйте позже.")
        print(f"Ошибка: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def handle_reply_button(call):
    user_id = call.data.split('_')[1]
    bot.answer_callback_query(call.id, "Введите текст ответа...")
    
    msg = bot.send_message(
        ADMIN_GROUP_ID,
        f"✍️ Введите ответ для пользователя ID `{user_id}`:",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, send_reply_to_user, user_id)

def send_reply_to_user(message, user_id):
    try:
        bot.send_message(
            int(user_id),
            f"📩 **Ответ от администратора:**\n\n{message.text}",
            parse_mode='Markdown'
        )
        bot.send_message(
            ADMIN_GROUP_ID,
            f"✅ **Ответ отправлен** пользователю `{user_id}`"
        )
    except Exception as e:
        bot.send_message(
            ADMIN_GROUP_ID,
            f"❌ **Ошибка:** {str(e)}"
        )

# Команда для просмотра статистики (только админ)
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id == ADMIN_GROUP_ID:
        active_users = len(user_last_message)
        bot.send_message(
            ADMIN_GROUP_ID,
            f"📊 **Статистика:**\n\n"
            f"👥 Активных пользователей за последние 5 минут: {active_users}\n"
            f"⏱️ Лимит: 1 сообщение / 5 секунд"
        )

print("🤖 БОТ ЗАПУЩЕН С ЗАЩИТОЙ ОТ СПАМА!")
print(f"Бот: @{bot.get_me().username}")
print(f"Лимит: 1 сообщение в 5 секунд на пользователя")

while True:
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(15)
