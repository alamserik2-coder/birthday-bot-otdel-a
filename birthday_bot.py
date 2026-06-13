
"""
Скрипт для отправки поздравления с днём рождения в Telegram-группу.
Запускается ОДИН РАЗ при каждом срабатывании по расписанию (GitHub Actions cron).

Для каждого нового бота (новой группы) создайте ОТДЕЛЬНЫЙ репозиторий
(или отдельную папку) с:
  - этим файлом (birthday_bot.py)
  - requirements.txt
  - birthdays.json со своим списком именинников
  - .github/workflows/birthday.yml со своим расписанием
  - своими секретами BOT_TOKEN и GROUP_ID в настройках репозитория

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

# Токен и ID берутся из переменных окружения (GitHub Secrets)
BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])

BIRTHDAYS_FILE = "birthdays.json"

# ========== ШАБЛОНЫ ПОЗДРАВЛЕНИЙ ==========
# {name} будет заменено на имя именинника

CONGRATS_TEMPLATES = [
    "🎉 Сегодня {name} отмечает свой день рождения! Поздравляем с этим прекрасным днём, желаем здоровья, счастья и успехов во всём! 🎂",
    "🥳 У нас сегодня особенный день — {name} отмечает день рождения! Пусть этот год принесёт много радости и добрых моментов! 🎈",
    "🎊 С днём рождения, {name}! Желаем крепкого здоровья, отличного настроения и исполнения всех желаний! 🎁",
    "🌟 Сегодня поздравляем {name} с днём рождения! Пусть впереди ждут только хорошие новости и приятные сюрпризы! 🎉",
    "🎂 {name}, поздравляем с днём рождения! Желаем благополучия, тепла в доме и улыбок каждый день! 🥂",
]


def load_birthdays(filepath: str) -> list:
    """Загружает список именинников из JSON файла.
    Формат файла: [{"name": "Имя Фамилия", "date": "DD-MM"}, ...]
    """
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
            try:
                await bot.send_message(chat_id=GROUP_ID, text=message)
                logger.info(f"Отправлено поздравление для {person['name']}")
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения: {e}")

    if not found:
        logger.info("Сегодня именинников нет")


if __name__ == "__main__":
    asyncio.run(main())
