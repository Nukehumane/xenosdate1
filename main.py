import telebot
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv # Нужно будет установить библиотеку (pip install python-dotenv)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)


# 📅 Настройка временных точек
tz = pytz.timezone("Europe/Moscow")

# Старт RP (1960 год)
xenos_start = datetime(1960, 2, 3, 0, 0)
xenos_start = tz.localize(xenos_start)

# Старт IRL (Твоя точка отсчета — теперь она не в будущем)
real_start = datetime(2026, 2, 3, 0, 0) 
real_start = tz.localize(real_start)

xenos_ratio = 30  # 1 день IRL = 30 дней RP (1 месяц)

# 🔧 Вычисление текущей Xenos-даты
def get_xenos_now():
    now_real = datetime.now(tz)
    delta_real = now_real - real_start
    # Считаем разницу в секундах и умножаем на 30
    xenos_seconds = delta_real.total_seconds() * xenos_ratio
    return xenos_start + timedelta(seconds=xenos_seconds)

# 🟢 /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, (
        "👋 Привет! Я бот для расчёта дат в мире Xenos RP.\n"
        "Бот работает локально на сервере.\n\n"
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
    )

# ⏳ /revers
@bot.message_handler(commands=['revers'])
def handle_revers(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Используй: /revers ДД.ММ.ГГГГ")
        return
    try:
        # Улучшенная обработка даты
        xenos_target = datetime.strptime(parts[1], "%d.%m.%Y")
        xenos_target = tz.localize(xenos_target)
        
        delta_xenos = xenos_target - xenos_start
        real_seconds = delta_xenos.total_seconds() / xenos_ratio
        real_time = real_start + timedelta(seconds=real_seconds)
        
        bot.reply_to(message, f"🕒 Эта дата в RP наступит в реальности: {real_time.strftime('%d.%m.%Y %H:%M')} (МСК)")
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка! Формат: ДД.ММ.ГГГГ (например: 01.05.1965)")

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
        xenos_seconds = delta_real.total_seconds() * xenos_ratio
        xenos_time = xenos_start + timedelta(seconds=xenos_seconds)
        
        bot.reply_to(message, f"📆 В реальности {parts[1]} будет соответствовать: {xenos_time.strftime('%d.%m.%Y %H:%M')} в RP")
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка! Формат: ДД.ММ.ГГГГ")

# 🚀 Запуск (БЕЗ FLASK)
if __name__ == "__main__":
    print(">>> Бот Xenos RP запущен на ПК!")
    print(">>> Нажмите Ctrl+C для остановки.")
    bot.infinity_polling()
    
