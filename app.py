import os
import logging
import requests
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Отключаем предупреждения SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        
        logger.info(f"Отправка запроса в Norge.ai: {user_message[:50]}...")
        
        response = requests.post(
            NORGE_API_URL,
            headers=headers,
            json=data,
            timeout=60,
            verify=False
        )
        
        logger.info(f"Статус ответа: {response.status_code}")
        logger.info(f"Текст ответа: {response.text[:200]}...")
        
        # Проверяем статус
        if response.status_code != 200:
            await update.message.reply_text(
                f"❌ Сервер вернул ошибку {response.status_code}. Попробуйте позже."
            )
            return
        
        # Проверяем, что ответ не пустой
        if not response.text or response.text.strip() == '':
            await update.message.reply_text(
                "❌ Сервер вернул пустой ответ. Попробуйте позже."
            )
            return
        
        # Пытаемся распарсить JSON
        try:
            result = response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            logger.error(f"Ответ сервера: {response.text[:500]}")
            await update.message.reply_text(
                "❌ Ошибка обработки ответа от сервера. Попробуйте позже."
            )
            return
        
        # Получаем ответ AI
        if 'choices' in result and len(result['choices']) > 0:
            ai_response = result['choices'][0]['message']['content']
        else:
            logger.error(f"Неожиданный формат ответа: {result}")
            await update.message.reply_text(
                "❌ Неожиданный формат ответа от сервера."
            )
            return
        
        # Обрезаем длинный ответ
        if len(ai_response) > 4000:
            ai_response = ai_response[:4000] + "...\n\n(Ответ обрезан)"
        
        await update.message.reply_text(ai_response)
        
    except requests.exceptions.Timeout:
        await update.message.reply_text(
            "⏰ Сервер долго не отвечает. Попробуйте позже."
        )
    except requests.exceptions.ConnectionError:
        await update.message.reply_text(
            "🔌 Ошибка соединения. Проверьте интернет."
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error: {e}")
        await update.message.reply_text(
            "❌ Ошибка соединения с сервером. Попробуйте позже."
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
    logger.info(f"API URL: {NORGE_API_URL}")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()