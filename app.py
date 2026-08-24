import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем ключи из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
NORGE_API_KEY = os.getenv('NORGE_API_KEY')
NORGE_API_URL = "https://api.norge.ai/v1/chat/completions"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "Привет! Я бот с искусственным интеллектом. Задай мне любой вопрос!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_message = update.message.text
    
    await update.message.chat.send_action(action="typing")
    
    try:
        headers = {
            'Authorization': f'Bearer {NORGE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': 'Ты полезный ассистент.'},
                {'role': 'user', 'content': user_message}
            ]
        }
        
        response = requests.post(NORGE_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        ai_response = response.json()['choices'][0]['message']['content']
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            "Извините, произошла ошибка. Попробуйте еще раз позже."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
    Доступные команды:
    /start - Начать общение
    /help - Показать справку
    
    Просто напишите сообщение, и я отвечу!
    """
    await update.message.reply_text(help_text)

def main():
    """Запуск бота (для локального запуска)"""
    if not TELEGRAM_TOKEN or not NORGE_API_KEY:
        logger.error("Отсутствуют необходимые токены!")
        return
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# ========== ДОБАВЬТЕ ЭТО ==========
# Для запуска через gunicorn на Render
app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
# ==================================

if __name__ == '__main__':
    main()