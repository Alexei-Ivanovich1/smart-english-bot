import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from config import BOT_TOKEN, CHANNEL_ID, CHANNEL_USERNAME

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== ПУТЬ К PDF ФАЙЛУ ==========
PDF_FILE_PATH = "harry_potter_chapter1.pdf"

# ========== ПРОВЕРКА ПОДПИСКИ ==========
async def check_subscription(user_id: int) -> bool:
    """Проверяет, подписан ли пользователь на канал"""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"   ⚠️ Ошибка проверки подписки: {e}")
        return False

# ========== КЛАВИАТУРЫ ==========
def get_main_keyboard():
    """Основная клавиатура"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📢 Подписаться на канал", 
                url=f"https://t.me/{CHANNEL_USERNAME[1:]}"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Проверить подписку", 
                callback_data="check_subscription"
            ),
            InlineKeyboardButton(
                text="📖 Скачать главу (PDF)", 
                callback_data="get_pdf"
            )
        ]
    ])
    return keyboard

# ========== КОМАНДА /START ==========
@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды /start"""
    welcome_text = f"""
🎉 *Smart English Bot с Гарри Поттером!*

Получите *первую главу* Гарри Поттера в *PDF формате* с иллюстрациями!

📌 *Условия:*
1. Подпишитесь на канал: {CHANNEL_USERNAME}
2. Нажмите "✅ Проверить подписку"
3. Скачайте PDF с адаптированным текстом

Уровень: Pre-Intermediate (A2-B1)
    """
    
    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

# ========== ПРОВЕРКА ПОДПИСКИ ==========
@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription_callback(callback: types.CallbackQuery):
    """Проверяет подписку пользователя"""
    user_id = callback.from_user.id
    username = callback.from_user.username or "без username"
    
    print(f"\n🔍 [{datetime.now()}] Проверка подписки от @{username} (ID: {user_id})")
    
    if await check_subscription(user_id):
        print(f"   ✅ Пользователь @{username} подписан на канал")
        await callback.answer("✅ Вы подписаны! Можете скачать PDF.", show_alert=True)
    else:
        print(f"   ❌ Пользователь @{username} НЕ подписан на канал")
        await callback.answer(
            f"❌ Вы не подписаны на {CHANNEL_USERNAME}",
            show_alert=True
        )

# ========== ОТПРАВКА PDF ==========
@dp.callback_query(lambda c: c.data == "get_pdf")
async def send_pdf_chapter(callback: types.CallbackQuery):
    """Отправляет PDF файл после проверки подписки"""
    user_id = callback.from_user.id
    username = callback.from_user.username or "без username"
    
    print(f"\n📥 [{datetime.now()}] Запрос PDF от @{username} (ID: {user_id})")
    
    # Проверяем подписку
    is_subscribed = await check_subscription(user_id)
    print(f"   🔍 Проверка подписки: {'✅ ПОДПИСАН' if is_subscribed else '❌ НЕ ПОДПИСАН'}")
    
    if not is_subscribed:
        await callback.answer(
            f"❌ Подпишитесь на {CHANNEL_USERNAME} сначала",
            show_alert=True
        )
        return
    
    print(f"   📁 Проверка файла {PDF_FILE_PATH}...")
    
    # Проверяем, существует ли файл
    if not os.path.exists(PDF_FILE_PATH):
        print(f"   ❌ Файл НЕ НАЙДЕН!")
        await callback.answer("❌ Файл PDF не найден", show_alert=True)
        await callback.message.answer(
            "Извините, файл временно недоступен. Администратор уведомлен."
        )
        return
    
    file_size = os.path.getsize(PDF_FILE_PATH)
    print(f"   ✅ Файл найден. Размер: {file_size} байт ({file_size/1024:.1f} KB)")
    
    try:
        print("   📤 Пытаюсь отправить файл...")
        
        # Используем FSInputFile (рекомендуется aiogram 3.x)
        from aiogram.types import FSInputFile
        
        document = FSInputFile(PDF_FILE_PATH)
        await bot.send_document(
            chat_id=callback.message.chat.id,
            document=document,
            caption="📖 *Harry Potter - Chapter 1 (B1 Level)*\n\n"
                   "Адаптированная первая глава с иллюстрациями.\n"
                   "Идеально для изучения английского!",
            parse_mode="Markdown",
          )
        
        print(f"   ✅ Файл успешно отправлен пользователю @{username}")
        await callback.answer("✅ PDF отправлен!")
        
    except Exception as e:
        print(f"   ❌ ОШИБКА отправки: {e}")
        print(f"   📍 Тип ошибки: {type(e).__name__}")
        
        # Детальный вывод ошибки
        import traceback
        traceback.print_exc()
        
        await callback.answer(f"❌ Ошибка при отправке файла", show_alert=True)

# ========== АДМИН КОМАНДЫ ==========
@dp.message(Command("upload_pdf"))
async def upload_pdf_command(message: types.Message):
    """Команда для загрузки нового PDF (только для админа)"""
    from config import ADMIN_ID
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("Эта команда только для администратора.")
        return
    
    if not message.document:
        await message.answer("Отправьте PDF файл как документ.")
        return
    
    if not message.document.file_name.endswith('.pdf'):
        await message.answer("Отправьте файл в формате PDF.")
        return
    
    try:
        # Скачиваем файл
        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        
        # Сохраняем как harry_potter_chapter1.pdf
        with open(PDF_FILE_PATH, "wb") as new_file:
            new_file.write(downloaded_file.read())
        
        file_size = os.path.getsize(PDF_FILE_PATH)
        print(f"\n📁 [{datetime.now()}] Админ обновил PDF. Новый размер: {file_size} байт")
        
        await message.answer(f"✅ PDF файл успешно обновлен! ({file_size/1024:.1f} KB)")
        
    except Exception as e:
        print(f"❌ Ошибка загрузки PDF админом: {e}")
        await message.answer(f"❌ Ошибка: {e}")

# ========== КОМАНДА /STATS ==========
@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    """Показывает статистику файла"""
    from config import ADMIN_ID
    
    if message.from_user.id != ADMIN_ID:
        return
    
    if os.path.exists(PDF_FILE_PATH):
        file_size = os.path.getsize(PDF_FILE_PATH)
        modified_time = datetime.fromtimestamp(os.path.getmtime(PDF_FILE_PATH))
        
        stats_text = f"""
📊 *Статистика файла:*

📁 Имя файла: `{PDF_FILE_PATH}`
📏 Размер: {file_size:,} байт ({file_size/1024:.1f} KB)
🕐 Последнее изменение: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}
✅ Существует: Да
        """
    else:
        stats_text = "❌ Файл PDF не найден!"
    
    await message.answer(stats_text, parse_mode="Markdown")

# ========== ЗАПУСК БОТА ==========
async def main():
    print("=" * 50)
    print("🤖 Бот 'Smart English Bot' запускается...")
    print(f"🕐 Время запуска: {datetime.now()}")
    print("=" * 50)
    
    print(f"📁 Проверяю PDF файл: {PDF_FILE_PATH}")
    print(f"📁 Абсолютный путь: {os.path.abspath(PDF_FILE_PATH)}")
    
    if os.path.exists(PDF_FILE_PATH):
        file_size = os.path.getsize(PDF_FILE_PATH)
        print(f"✅ Файл найден! Размер: {file_size:,} байт ({file_size/1024:.1f} KB)")
    else:
        print("❌ ФАЙЛ НЕ НАЙДЕН!")
        print("   Положите harry_potter_chapter1.pdf в папку с ботом")
    
    print("=" * 50)
    print("🚀 Бот запущен и готов к работе!")
    print("=" * 50)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())