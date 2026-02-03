from flask import Flask, request
import telebot
from datetime import datetime, timedelta
import pytz
import os
import time

# 🔐 Токен Telegram-бота
TOKEN = os.getenv("TOKEN") or "8373973529:AAGAZpY1ApgypN0ZIL9Cphk7AMO9gkvCX0k"
bot = telebot.TeleBot(TOKEN, parse_mode=None)
app = Flask(__name__)

# 📅 Настройка временных точек (ориентир строго по МСК)
tz = pytz.timezone("Europe/Moscow")
xenos_start = datetime(1960, 2, 3, 0, 0, tzinfo=tz)   # старт RP
real_start = datetime(2026, 2, 3, 0, 0, tzinfo=tz)    # старт IRL
xenos_ratio = 30  # 1 день IRL = 30 дней RP (1 месяц)

# 🔧 Вычисление текущей Xenos-даты
def get_xenos_now():
    now_real = datetime.now(tz)
    delta_real = now_real - real_start
    delta_minutes = delta_real.total_seconds() / 60
    xenos_minutes = delta_minutes * xenos_ratio
    return xenos_start + timedelta(minutes=xenos_minutes)

# 🟢 /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, (
        "👋 Привет! Я бот для расчёта дат в мире Xenos RP.\n\n"
        "Доступные команды:\n"
        "/xenos_now — текущая дата в Xenos RP\n"
        "/revers ДД.ММ.ГГГГ — когда наступит Xenos-дата в реальности\n"
        "/convert ДД.ММ.ГГГГ — какая Xenos-дата соответствует реальной\n"
    ))

# 📅 /xenos_now
@bot.message_handler(commands=['xenos_now'])
def handle_now(message):
    xenos_time = get_xenos_now()
    bot.reply_to(
        message,
        f"📅 Сейчас в мире Xenos RP: {xenos_time.strftime('%H:%M %d.%m.%Y')} (МСК)"
        
# ⏳ /revers
@bot.message_handler(commands=['revers'])
def handle_revers(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Используй: /revers ДД.ММ.ГГГГ")
        return
    try:
        xenos_target = datetime.strptime(parts[1], "%d.%m.%Y")
        xenos_target = tz.localize(xenos_target)
        delta_xenos = xenos_target - xenos_start
        delta_minutes = delta_xenos.total_seconds() / 60
        real_minutes = delta_minutes / xenos_ratio
        real_time = real_start + timedelta(minutes=real_minutes)
        bot.reply_to(message, f"🕒 Эта дата в Xenos RP наступит в реальном мире: {real_time.strftime('%d.%m.%Y %H:%M')} (МСК)")
    except Exception as e:
        print("Ошибка в /revers:", e)
        bot.reply_to(message, "❌ Неверный формат. Используй: /revers ДД.ММ.ГГГГ")

# 🔄 /convert
@bot.message_handler(commands=['convert'])
def handle_convert(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Используй: /convert ДД.ММ.ГГГГ")
        return
    try:
        real_target = datetime.strptime(parts[1], "%d.%m.%Y")
        real_target = tz.localize(real_target)
        delta_real = real_target - real_start
        delta_minutes = delta_real.total_seconds() / 60
        xenos_minutes = delta_minutes * xenos_ratio
        xenos_time = xenos_start + timedelta(minutes=xenos_minutes)
        bot.reply_to(message, f"📆 Эта дата в реальности соответствует: {xenos_time.strftime('%d.%m.%Y %H:%M')} в Xenos RP (МСК)")
    except Exception as e:
        print("Ошибка в /convert:", e)
        bot.reply_to(message, "❌ Неверный формат. Используй: /convert ДД.ММ.ГГГГ")

# 📡 POST-запрос от Telegram
@app.route("/", methods=["POST"])
def webhook():
    try:
        start = time.time()
        raw = request.stream.read().decode("utf-8")
        print("RAW update:", raw)
        update = telebot.types.Update.de_json(raw)
        print("Parsed update:", update)
        bot.process_new_updates([update])
        print("Processed in", round(time.time() - start, 2), "seconds")
    except Exception as e:
        print("Webhook error:", e)
    return "OK", 200

# 🌐 GET-запрос от браузера
@app.route("/", methods=["GET"])
def index():
    return "Xenos RP bot is alive!", 200
