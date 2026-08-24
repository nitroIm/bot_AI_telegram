import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота из переменных окружения
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден! Добавьте переменную окружения BOT_TOKEN на Render.")

# Простой "разговорник" (словарь с ответами)
CONVERSATIONS = {
    "привет": "Привет! 👋 Как у тебя дела?",
    "как дела": "У меня всё отлично! А у тебя? 😊",
    "что ты умеешь": "Я простой бот-разговорник. Могу:\n- Отвечать на приветствия\n- Рассказывать анекдоты\n- Давать советы\n- И просто болтать!",
    "анекдот": "Шутка: Почему программисты путают Хэллоуин и Рождество? Потому что 31 окт = 25 дек! 😄",
    "совет": "Мой совет: всегда делай бэкапы! 💾 И не забывай пить воду 💧",
    "пока": "Пока! Было приятно поболтать! 👋 До встречи!",
    "спасибо": "Пожалуйста! Всегда рад помочь! 🤝",
    "как тебя зовут": "Меня зовут Ботик! 🤖 Я твой виртуальный друг.",
}

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        "Я простой бот-разговорник. Я умею:\n"
        "• Отвечать на простые фразы\n"
        "• Рассказывать анекдоты\n"
        "• Давать советы\n\n"
        "Просто напиши мне что-нибудь!\n"
        "Например: 'привет', 'анекдот', 'совет'",
        reply_markup=get_main_keyboard()
    )

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Мои команды:\n\n"
        "/start - начать общение\n"
        "/help - показать справку\n"
        "/info - информация о боте\n"
        "/clear - очистить диалог\n\n"
        "Или просто напиши мне фразу!"
    )

# Обработчик команды /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Бот-разговорник\n"
        "Версия: 1.0\n"
        "Создан для демонстрации работы на Render\n"
        "Использует python-telegram-bot"
    )

# Обработчик команды /clear (очищает диалог)
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Просто очищаем контекст (если есть сохранённые данные)
    context.user_data.clear()
    await update.message.reply_text("🧹 Диалог очищен! Можем начать заново.")

# Клавиатура для быстрого доступа
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("👋 Привет"), KeyboardButton("😄 Анекдот")],
        [KeyboardButton("💡 Совет"), KeyboardButton("ℹ️ Информация")],
        [KeyboardButton("👋 Пока")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Основной обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower().strip()
    user_name = update.effective_user.first_name
    
    logger.info(f"Сообщение от {user_name}: {user_text}")
    
    # Проверка на кнопки клавиатуры (с эмодзи)
    if "👋 привет" in user_text:
        user_text = "привет"
    elif "😄 анекдот" in user_text:
        user_text = "анекдот"
    elif "💡 совет" in user_text:
        user_text = "совет"
    elif "ℹ️ информация" in user_text:
        await info(update, context)
        return
    elif "👋 пока" in user_text:
        user_text = "пока"
    
    # Поиск ответа в "разговорнике"
    response = None
    for key, value in CONVERSATIONS.items():
        if key in user_text:
            response = value
            break
    
    # Если ответ найден - отправляем
    if response:
        await update.message.reply_text(response, reply_markup=get_main_keyboard())
    else:
        # Если не нашли - умный ответ
        responses = [
            f"Интересно, {user_name}! Расскажи ещё что-нибудь 😊",
            "Я тебя слушаю! 👂 Что ещё хочешь узнать?",
            "Ого! А ты умеешь задавать вопросы 😄",
            "Продолжай, мне интересно! 🤔",
            "Я ещё учусь, но стараюсь помогать! 📚"
        ]
        import random
        await update.message.reply_text(
            random.choice(responses),
            reply_markup=get_main_keyboard()
        )

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")

def main():
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    # Запуск (polling - подходит для Render)
    logger.info("🤖 Бот запущен и работает!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()