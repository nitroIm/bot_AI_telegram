from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NEUROGATE_KEY = os.getenv("NEUROGATE_KEY")
# Получаем порт, который выделяет Render (это критически важно)
PORT = int(os.environ.get('PORT', 8080))
# Ваш URL (как в логах)
RENDER_URL = "https://bot-ai-telegram.onrender.com"

client = OpenAI(
    api_key=NEUROGATE_KEY,
    base_url="https://api.neurogate.space/v1"
)

async def handle_message(update: Update, context):
    user_msg = update.message.text
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": user_msg}]
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Обработчик для проверки, что бот жив
async def start(update: Update, context):
    await update.message.reply_text("Бот запущен и работает!")

# Эндпоинт для Telegram (Telegram будет присылать сюда сообщения)
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok"

# Эндпоинт при открытии сайта (для проверки Render)
@app.route('/')
def home():
    return "Бот работает!"

# Инициализируем приложение (глобально, чтобы Flask мог его видеть в webhook)
application = Application.builder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    # Устанавливаем связь с Telegram (Webhook)
    application.bot.set_webhook(url=f"{RENDER_URL}/{TELEGRAM_TOKEN}")
    # Запускаем Flask (это удерживает сервис живым и принимает запросы от Telegram)
    app.run(host="0.0.0.0", port=PORT)