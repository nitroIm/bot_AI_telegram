from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NEUROGATE_KEY = os.getenv("NEUROGATE_KEY")

@app.route('/')
def home():
    return "Бот работает!"

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

def run_bot():
    bot_app = Application.builder().token(TELEGRAM_TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.run_polling()

if __name__ == "__main__":
    thread = Thread(target=run_bot)
    thread.start()
    app.run(host="0.0.0.0", port=8080)