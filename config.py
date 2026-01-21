import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Токен вашего бота (должен быть в .env файле)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ваш Telegram канал для привлечения подписчиков
CHANNEL_USERNAME = "@englishpro77"  

# ID вашего канала (можно получить через бота @username_to_id_bot)
CHANNEL_ID_STR = os.getenv("CHANNEL_ID", "-1001154836567")
CHANNEL_ID = int(CHANNEL_ID_STR) if CHANNEL_ID_STR else -1001154836567

# Ваш Telegram ID (для админ-команд)
ADMIN_ID_STR = os.getenv("ADMIN_ID", "349307908")
ADMIN_ID = int(ADMIN_ID_STR) if ADMIN_ID_STR else 349307908

# Настройки базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///english_bot.db")