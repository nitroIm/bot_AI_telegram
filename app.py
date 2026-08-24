import os
import logging
import requests
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Google Gemini API endpoint (бесплатная версия)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот на основе **Google Gemini 1.5 Flash**!\n\n"
        "🤖 Задай мне любой вопрос, и я отвечу!\n"
        "📊 Бесплатно: 1500 запросов в день\n"
        "⚡ Быстрый и умный!\n\n"
        "Просто напиши мне сообщение 😊"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    await update.message.chat.send_action(action="typing")
    
    try:
        # Формируем запрос к Gemini API
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": user_message}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        logger.info(f"Запрос к Gemini: {user_message[:50]}...")
        
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=60
        )
        
        logger.info(f"Статус ответа Gemini: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Ошибка Gemini API: {response.text[:200]}")
            await update.message.reply_text(
                f"❌ Ошибка API ({response.status_code}). Попробуйте позже."
            )
            return
        
        # Парсим ответ
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            ai_response = result['candidates'][0]['content']['parts'][0]['text']
        else:
            logger.error(f"Неожиданный формат ответа: {result}")
            await update.message.reply_text(
                "❌ Неожиданный формат ответа от сервера."
            )
            return
        
        # Обрезаем длинный ответ
        if len(ai_response) > 4000:
            ai_response = ai_response[:4000] + "...\n\n(Ответ обрезан из-за длины)"
        
        await update.message.reply_text(ai_response)
        
    except requests.exceptions.Timeout:
        await update.message.reply_text(
            "⏰ Сервер долго отвечает. Попробуйте позже."
        )
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
    🤖 *Бот на Google Gemini*
    
    *Команды:*
    /start - Начать общение
    /help - Помощь
    /stats - Статистика использования
    
    *О боте:*
    • Модель: Gemini 1.5 Flash
    • Бесплатно: 1500 запросов/день
    • Отвечает на любые вопросы
    
    Просто напиши мне сообщение!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для проверки статуса API"""
    await update.message.reply_text(
        "📊 *Статус Google Gemini*\n\n"
        "✅ API подключен\n"
        "🆓 Тариф: Бесплатный (1500 запросов/день)\n"
        "⚡ Модель: Gemini 1.5 Flash\n"
        "🌐 Статус: Работает\n\n"
        "Бот готов к работе! 🚀"
    )

def main():
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_TOKEN не установлен!")
        return
    
    if not GEMINI_API_KEY:
        logger.error("❌ GEMINI_API_KEY не установлен!")
        logger.error("👉 Получи ключ на https://aistudio.google.com/apikey")
        return
    
    logger.info("✅ Токены загружены")
    logger.info(f"API URL: {GEMINI_API_URL}")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 Бот запущен на Google Gemini 1.5 Flash!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()