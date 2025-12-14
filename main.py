from flask import Flask, request
import telebot
from datetime import datetime, timedelta
import pytz
import os

# Получаем токен из переменной окружения
TOKEN = os.getenv("TOKEN") or "8373973529:AAGAZpY1ApgypN0ZIL9Cphk7AMO9gkvCX0k"
bot = telebot.TeleBot(TOKEN, parse_mode=None)
app = Flask(__name__)

# Настройка временных точек
xenos_start = datetime(1990, 12, 1, 0, 0)
real_start = datetime(2025, 12, 1, 0, 0, tzinfo=pytz.timezone("Europe/Moscow"))

# 1 реальный день = 90 Xenos-дней
xenos_per_real_minute = 90 * 24 * 60 / (24 * 60)

# Вычисление текущей Xenos-даты
def get_xenos_now():
    now_real = datetime.now(pytz.timezone("Europe/Moscow"))
    delta_real = now_real - real_start
    delta_minutes = delta_real.total_seconds() / 60
    xenos_minutes = delta_minutes * xenos_per_real_minute
    return xenos_start + timedelta(minutes=xenos_minutes)

# Команда /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, (
        "👋 Привет! Я бот для расчёта дат в мире Xenos RP.\n\n"
        "Доступные команды:\n"
        "/xenos_now — текущая дата в Xenos RP\n"
        "/revers ДД.ММ.ГГГГ — когда наступит Xenos-дата в реальности\n"
        "/convert ДД.ММ.ГГГГ — какая Xenos-дата соответствует реальной\n"
    ))

# Команда /xenos_now
@bot.message_handler(commands=['xenos_now'])
def handle_now(message):
    xenos_time = get_xenos_now()
    bot.reply_to(message, f"📅 Сейчас в мире Xenos RP: {xenos_time.strftime('%d.%m.%Y %H:%M')}")

# Команда /revers
@bot.message_handler(commands=['revers'])
def handle_revers(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Используй: /revers ДД.ММ.ГГГГ")
        return
    try:
        xenos_target = datetime.strptime(parts[1], "%d.%m.%Y")
        delta_xenos = xenos_target - xenos_start
        delta_minutes = delta_xenos.total_seconds() / 60
        real_minutes = delta_minutes / xenos_per_real_minute
        real_time = real_start + timedelta(minutes=real_minutes)
        bot.reply_to(message, f"🕒 Эта дата в Xenos RP наступит в реальном мире: {real_time.strftime('%d.%m.%Y %H:%M')} (МСК)")
    except Exception:
        bot.reply_to(message, "❌ Неверный формат. Используй: /revers ДД.ММ.ГГГГ")

# Команда /convert
@bot.message_handler(commands=['convert'])
def handle_convert(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Используй: /convert ДД.ММ.ГГГГ")
        return
    try:
        real_target = datetime.strptime(parts[1], "%d.%m.%Y")
        real_target = pytz.timezone("Europe/Moscow").localize(real_target)
        delta_real = real_target - real_start
        delta_minutes = delta_real.total_seconds() / 60
        xenos_minutes = delta_minutes * xenos_per_real_minute
        xenos_time = xenos_start + timedelta(minutes=xenos_minutes)
        bot.reply_to(message, f"📆 Эта дата в реальности соответствует: {xenos_time.strftime('%d.%m.%Y %H:%M')} в Xenos RP")
    except Exception:
        bot.reply_to(message, "❌ Неверный формат. Используй: /convert ДД.ММ.ГГГГ")

# Обработка входящих запросов от Telegram
@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200
@app.route("/", methods=["GET"])
def index():
    return "Xenos RP bot is alive!", 200
