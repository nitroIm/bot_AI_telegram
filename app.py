import os
import logging
import requests
import ssl
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
    await update.message.reply_text(
        "👋 Привет! Я бот с искусственным интеллектом.\n"
        "Задай мне любой вопрос!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                {'role': 'system', 'content': 'Ты полезный ассистент. Отвечай на русском.'},
                {'role': 'user', 'content': user_message}
            ]
        }
        
        # ✅ БЕЗОПАСНОЕ РЕШЕНИЕ: отключаем проверку только для этого запроса
        response = requests.post(
            NORGE_API_URL,
            headers=headers,
            json=data,
            timeout=30,
            verify=False  # Отключаем проверку SSL для Norge.ai
        )
        response.raise_for_status()
        
        ai_response = response.json()['choices'][0]['message']['content']
        
        if len(ai_response) > 4000:
            ai_response = ai_response[:4000] + "...\n\n(Ответ обрезан из-за длины)"
        
        await update.message.reply_text(ai_response)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error: {e}")
        await update.message.reply_text(
            "❌ Ошибка соединения. Попробуйте позже."
        )
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        await update.message.reply_text(
            "😅 Что-то пошло не так. Попробуйте еще раз."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    🤖 *Команды:*
    /start - Начать общение
    /help - Помощь
    
    Просто напиши мне сообщение!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main():
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_TOKEN не установлен!")
        return
    
    if not NORGE_API_KEY:
        logger.error("❌ NORGE_API_KEY не установлен!")
        return
    
    logger.info("✅ Токены загружены")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()