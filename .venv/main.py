import asyncio
import httpx
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv

# --- Загрузка переменных из .env ---
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# --- Инициализация ---
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- Функции ---
async def get_weather(city: str) -> str:
    """Получает погоду для указанного города."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            weather_description = data.get('weather', [{}])[0].get('description', 'нет данных')
            temp = data.get('main', {}).get('temp', 'нет данных')
            feels_like = data.get('main', {}).get('feels_like', 'нет данных')
            humidity = data.get('main', {}).get('humidity', 'нет данных')
            wind_speed = data.get('wind', {}).get('speed', 'нет данных')

            return (
                f"Погода в городе {city.capitalize()}:\n"
                f"🌡️ Температура: {temp}°C (ощущается как {feels_like}°C)\n"
                f"🌬️ Ветер: {wind_speed} м/с\n"
                f"💧 Влажность: {humidity}%\n"
                f"☁️ Описание: {weather_description.capitalize()}"
            )
        except httpx.HTTPStatusError:
            return f"Не удалось найти город '{city}'. Попробуйте еще раз."
        except Exception as e:
            logging.error(f"Ошибка при запросе к API погоды: {e}")
            return "Произошла ошибка при получении данных о погоде."

# --- Обработчики ---
@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply("Привет! 👋\nЯ бот для погоды. Просто отправь мне название города.")

@dp.message()
async def send_weather_info(message: types.Message):
    city = message.text
    weather_report = await get_weather(city)
    await message.answer(weather_report)

# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
