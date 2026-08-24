import os
import logging
import requests
import ssl
import certifi
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

# Создаем сессию с безопасными настройками
session = requests.Session()
session.verify = certifi.where()  # Используем актуальные сертификаты

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "👋 Привет! Я бот с искусственным интеллектом.\n"
        "Задай мне любой вопрос, и я постараюсь помочь!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_message = update.message.text
    
    # Показываем, что бот печатает
    await update.message.chat.send_action(action="typing")
    
    try:
        headers = {
            'Authorization': f'Bearer {NORGE_API_KEY}',
            'Content-Type': 'application/json',
            'User-Agent': 'TelegramBot/1.0'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': 'Ты полезный и вежливый ассистент. Отвечай на русском языке.'},
                {'role': 'user', 'content': user_message}
            ],
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        # Безопасный запрос с проверкой SSL
        response = session.post(
            NORGE_API_URL,
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # Ограничиваем длину ответа (Telegram лимит ~4096 символов)
        if len(ai_response) > 4000:
            ai_response = ai_response[:4000] + "...\n\n(Ответ слишком длинный, я его обрезал)"
        
        await update.message.reply_text(ai_response)
        
    except requests.exceptions.SSLError as e:
        logger.error(f"SSL Error: {e}")
        await update.message.reply_text(
            "🔒 Ошибка безопасности соединения. Попробуйте позже."
        )
    except requests.exceptions.Timeout:
        await update.message.reply_text(
            "⏰ Сервер не отвечает. Попробуйте позже."
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error: {e}")
        await update.message.reply_text(
            "❌ Ошибка соединения с AI сервером. Попробуйте позже."
        )
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        await update.message.reply_text(
            "😅 Что-то пошло не так. Попробуйте еще раз."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
    🤖 *Доступные команды:*
    
    /start - Начать общение
    /help - Показать эту справку
    /about - Информация о боте
    
    *Как использовать:*
    Просто напишите мне любое сообщение, и я отвечу с помощью AI!
    
    *Примеры:*
    • "Расскажи о космосе"
    • "Как приготовить пиццу?"
    • "Реши математическую задачу"
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /about"""
    about_text = """
    🤖 *О боте:*
    
    Этот бот использует искусственный интеллект 
    для ответа на ваши вопросы.
    
    *Технологии:*
    • Python 3.11
    • Telegram Bot API
    • Norge.ai API
    
    *Безопасность:*
    🔒 Все соединения защищены SSL/TLS
    🔑 Токены хранятся в переменных окружения
    🛡️ Никакие данные не сохраняются
    
    Сделано с ❤️
    """
    await update.message.reply_text(about_text, parse_mode='Markdown')

def main():
    """Запуск бота"""
    # Проверяем наличие токенов
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_TOKEN не установлен!")
        return
    
    if not NORGE_API_KEY:
        logger.error("❌ NORGE_API_KEY не установлен!")
        return
    
    logger.info("✅ Все токены загружены")
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("🚀 Бот запущен и готов к работе!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()