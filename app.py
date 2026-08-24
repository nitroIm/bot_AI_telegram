import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NEUROGATE_KEY = os.getenv("NEUROGATE_KEY")
PORT = int(os.environ.get('PORT', 8080))
URL = "https://bot-ai-telegram.onrender.com"

client = OpenAI(
    api_key=NEUROGATE_KEY,
    base_url="https://api.neurogate.space/v1"
)

application = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("Бот запущен!")

async def handle_message(update: Update, context):
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": update.message.text}]
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Эндпоинт для Telegram (именно здесь должен быть POST, иначе будет 405)
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok"

# Эндпоинт для проверки Render (GET)
@app.route("/", methods=["GET"])
def home():
    return "Бot работает!"

if __name__ == "__main__":
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Установка вебхука (сразу подключаем Telegram к нашему пути)
    application.bot.set_webhook(url=f"{URL}/{TELEGRAM_TOKEN}")
    
    app.run(host="0.0.0.0", port=PORT)