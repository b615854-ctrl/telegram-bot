import telebot
import os
import time

# Токен второго бота (получите у @BotFather)
TOKEN = '8681961770:AAFuVjp8ynlIZyJ4iU6uaJbbIljyAY61hLg'

# Ссылка на закрытый канал
CHANNEL_LINK = 'https://t.me/+63uqWdYMhZJjNTYy'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_link(message):
    user_name = message.from_user.first_name
    bot.reply_to(
        message,
        f"👋 Привет, {user_name}!\n\n"
        f"Вот ссылка на наш закрытый канал:\n"
        f"{CHANNEL_LINK}\n\n"
        f"Нажмите на ссылку, чтобы присоединиться 🔗"
    )

# Обработка обычных сообщений (просто напоминание)
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(
        message,
        "Отправьте /start, чтобы получить ссылку на канал 📢"
    )

print("🤖 БОТ-ССЫЛКА ЗАПУЩЕН!")
print(f"Бот: @{bot.get_me().username}")
print(f"Канал: {CHANNEL_LINK}")

while True:
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(15)
