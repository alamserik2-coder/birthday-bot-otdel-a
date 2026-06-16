"""
Скрипт для отправки поздравления с днём рождения в Telegram-группу.
Если у именинника указано фото - отправляется фото с подписью.
Если фото нет - отправляется обычное текстовое сообщение.

Запускается ОДИН РАЗ при каждом срабатывании по расписанию (GitHub Actions cron).

Формат birthdays.json:
[
  {"name": "Имя Фамилия", "date": "DD-MM", "photo": "photos/имя.jpg"},
  {"name": "Имя2", "date": "DD-MM"}
]

Поле "photo" необязательно - указывайте путь к файлу внутри репозитория
(например, в папке photos/), если хотите отправлять фото именинника.

Токен и ID группы берутся из переменных окружения (Secrets),
не хранить их прямо в коде!
"""

import json
import random
import logging
import os
import asyncio
from datetime import datetime
from telegram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== НАСТРОЙКИ ==========

BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])

BIRTHDAYS_FILE = "birthdays.json"

# ========== ШАБЛОНЫ ПОЗДРАВЛЕНИЙ ==========
# {name} будет заменено на имя именинника

CONGRATS_TEMPLATES = [
    "🎉 Сегодня день рождения у {name}! Поздравляем от всей группы с этим прекрасным днём, желаем здоровья, счастья и успехов во всём! 🎂",
    "🥳 У нас сегодня особенный день — {name} отмечает день рождения! Пусть этот год принесёт много радости и добрых моментов! Поздравляем от всей группы! 🎈",
    "🎊 С днём рождения, {name}! Желаем крепкого здоровья, отличного настроения и исполнения всех желаний! Поздравляем от всей группы!🎁",
    "🌟 Сегодня поздравляем {name} с днём рождения! Пусть впереди ждут только хорошие новости и приятные сюрпризы! Поздравляем от всей группы!🎉",
    "🎂 {name}, поздравляем с днём рождения! Желаем благополучия, тепла в доме и улыбок каждый день! Поздравляем от всей группы!🥂",
]


def load_birthdays(filepath: str) -> list:
    """Загружает список именинников из JSON файла."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Файл {filepath} не найден, возвращаю пустой список")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка чтения {filepath}: {e}")
        return []


async def main():
    today = datetime.now().strftime("%d-%m")
    logger.info(f"Проверка именинников на {today}")

    birthdays = load_birthdays(BIRTHDAYS_FILE)
    bot = Bot(token=BOT_TOKEN)

    found = False
    for person in birthdays:
        if person.get("date") == today:
            found = True
            template = random.choice(CONGRATS_TEMPLATES)
            message = template.format(name=person["name"])
            photo_path = person.get("photo")
          
            # Добавляем возраст, если указан год рождения
            year = person.get("year")
            if year:
                age = now.year - year
                message += f"\nСегодня исполняется {age} лет! 🎈"
            photo_path = person.get("photo")

            try:
                if photo_path and os.path.exists(photo_path):
                    with open(photo_path, "rb") as photo_file:
                        await bot.send_photo(
                            chat_id=GROUP_ID,
                            photo=photo_file,
                            caption=message,
                        )
                    logger.info(f"Отправлено поздравление с фото для {person['name']}")
                else:
                    if photo_path:
                        logger.warning(f"Фото не найдено по пути: {photo_path}")
                    await bot.send_message(chat_id=GROUP_ID, text=message)
                    logger.info(f"Отправлено текстовое поздравление для {person['name']}")
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения для {person['name']}: {e}")

    if not found:
        logger.info("Сегодня именинников нет")


if __name__ == "__main__":
    asyncio.run(main())

   
