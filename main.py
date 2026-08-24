import logging
import os
import requests
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

# Забираем токен бота и ключ Neurogate из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
NEUROGATE_API_KEY = os.getenv("NEUROGATE_API_KEY")

if not BOT_TOKEN:
    logging.error("BOT_TOKEN не найден в переменных окружения")
    raise SystemExit("Установи переменную окружения BOT_TOKEN")

if not NEUROGATE_API_KEY:
    logging.error("NEUROGATE_API_KEY не найден в переменных окружения")
    raise SystemExit("Установи переменную окружения NEUROGATE_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ===== ФУНКЦИЯ ВЫЗОВА NEUROGATE API =====
def ask_neurogate(user_text: str) -> str:
    """
    Отправляем текст пользователя в Neurogate
    и возвращаем ответ ассистента как строку.
    """

    # ВАЖНО: сюда вставь правильный URL и формат под свой API Neurogate.
    # Я даю примерный формат. В кабинете Neurogate смотри раздел API/Docs
    # и скорректируй endpoint/поля, если нужно.

    url = "https://api.neurogate.ai/v1/chat/completions"  # примерный адрес

    headers = {
        "Authorization": f"Bearer {NEUROGATE_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-4o-mini",  # или другая модель из документации Neurogate
        "messages": [
            {"role": "system", "content": "Ты ассистент Neurogate в Telegram-боте."},
            {"role": "user", "content": user_text},
        ],
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Здесь нужно вытащить текст ответа из структуры data
        # Формат зависит от API Neurogate. Часто бывает примерно так:
        #
        # data["choices"][0]["message"]["content"]
        #
        # Если формат другой — зайди в документацию и подправь нужное место.

        answer = (
            data["choices"][0]["message"]["content"]
            if "choices" in data
            else "Не удалось разобрать ответ от Neurogate."
        )

        return answer

    except Exception as e:
        logging.exception("Ошибка при запросе к Neurogate API")
        return f"Произошла ошибка при обращении к Neurogate: {e}"

# ===== ОБРАБОТЧИКИ TELEGRAM =====

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот на базе Neurogate.\n"
        "Напиши мне вопрос или текст — я отвечу с помощью ИИ."
    )

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    user_text = message.text

    # Сообщение “думаю…”
    waiting_msg = await message.answer("Думаю над ответом...")

    # Спрашиваем Neurogate
    answer = ask_neurogate(user_text)

    # Отправляем ответ
    await message.answer(answer)

    # Удаляем промежуточное сообщение (по желанию)
    try:
        await waiting_msg.delete()
    except Exception:
        pass

if __name__ == "__main__":
    logging.info("Бот запускается (long polling)...")
    executor.start_polling(dp, skip_updates=True)