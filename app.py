Import os 
from flask import Flask
from threading import Thread
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI

# ===== НАСТРОЙКИ (ПОМЕНЯЙТЕ) =====

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NEUROGATE_KEY = os.getenv("NEUROGATE_KEY")

# =================================

app = Flask(__name__)

# Заглушка для Render (чтобы не падал)
@app.route('/')
def home():
    return "Бот работает!"

# Инициализация OpenAI (Neurogate)
client = OpenAI(
    api_key=NEUROGATE_KEY,
    base_url="https://api.neurogate.space/v1"
)

# Обработчик сообщений
async def handle_message(update: Update, context):
    user_msg = update.message.text
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",  # Модель DeepSeek
            messages=[{"role": "user", "content": user_msg}],
            max_tokens=1500
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Функция запуска бота
def run_bot():
    bot_app = Application.builder().token(TELEGRAM_TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.run_polling()

# Запуск бота в фоновом потоке (чтобы Flask не блокировал)
def start_bot_thread():
    thread = Thread(target=run_bot)
    thread.start()

# Главная точка входа для Render
if __name__ == "__main__":
    start_bot_thread()
    app.run(host="0.0.0.0", port=8080)