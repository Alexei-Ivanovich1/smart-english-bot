import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Токен вашего бота (должен быть в .env файле)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ваш Telegram канал для привлечения подписчиков
# ЗАМЕНИТЕ на username вашего реального канала (начинается с @)
CHANNEL_USERNAME = "@englishpro77"  # ← ЗАМЕНИТЕ ЭТО!

# ID вашего канала (можно получить через бота @username_to_id_bot)
# Пока оставьте пустым, позже получите
CHANNEL_ID = -1001154836567  # ← ПОТОМ ЗАМЕНИТЕ

# Ваш Telegram ID (для админ-команд)
ADMIN_ID = 349307908  # Ваш ID

# Настройки базы данных
DATABASE_URL = "sqlite:///english_bot.db"