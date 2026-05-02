import telebot
from groq import Groq
import requests
from datetime import datetime
import pytz

TELEGRAM_TOKEN = "8490178133:AAHXZndETwFxpFzqmrsPZeYyjN4DL-_7YY0"
GROQ_API_KEY = "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"
ADMIN_ID = 8186356900

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

chat_histories = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! 👋 Men Abram tomonidan yartilgan sizni shaxsiy AI botiman!\n\n/help — buyruqlar ro'yxati")
    if message.chat.id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"🆕 Yangi foydalanuvchi: {message.from_user.first_name} (@{message.from_user.username})")

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, """📋 Buyruqlar:
/start — Botni boshlash
/help — Buyruqlar
/joke — Hazil aytib ber
/tarjima [matn] — Tarjima qil
/havo [shahar] — Ob-havo
/soat — Hozirgi vaqt
/clear — Tarixni tozala""")

@bot.message_handler(commands=['soat'])
def soat(message):
    toshkent = pytz.timezone('Asia/Tashkent')
    vaqt = datetime.now(toshkent).strftime("%H:%M:%S")
    sana = datetime.now(toshkent).strftime("%d.%m.%Y")
    bot.reply_to(message, f"🕐 Hozirgi vaqt: {vaqt}\n📅 Sana: {sana}")

@bot.message_handler(commands=['joke'])
def joke(message):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Menga bitta qisqa va kulgili o'zbek hazili ayt"}]
    )
    bot.reply_to(message, response.choices[0].message.content)

@bot.message_handler(commands=['tarjima'])
def tarjima(message):
    text = message.text.replace('/tarjima', '').strip()
    if not text:
        bot.reply_to(message, "Tarjima qilish uchun: /tarjima [matn]")
        return
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"Shu matnni ingliz tiliga tarjima qil: {text}"}]
    )
    bot.reply_to(message, response.choices[0].message.content)

@bot.message_handler(commands=['havo'])
def havo(message):
    shahar = message.text.replace('/havo', '').strip()
    if not shahar:
        bot.reply_to(message, "Shahar nomini yozing: /havo Toshkent")
        return
    try:
        url = f"https://wttr.in/{shahar}?format=3&lang=uz"
        r = requests.get(url)
        bot.reply_to(message, f"🌤️ {r.text}")
    except:
        bot.reply_to(message, "Ob-havo ma'lumotini ololmadim 😕")

@bot.message_handler(commands=['clear'])
def clear(message):
    chat_histories[message.chat.id] = []
    bot.reply_to(message, "✅ Suhbat tarixi tozalandi!")

@bot.message_handler(func=lambda m: True)
def handle(message):
    user_id = message.chat.id
    if user_id not in chat_histories:
        chat_histories[user_id] = []

    chat_histories[user_id].append({
        "role": "user",
        "content": message.text
    })

    bot.send_chat_action(user_id, 'typing')

    if user_id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"👤 {message.from_user.first_name}: {message.text}")

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Siz Abram Iskandarov yaratgan shaxsiy AI assistantsiz. Hech qachon boshqa kompaniya yaratgan dema. O'zbek tilida, qisqa va aniq javob ber. Abram haqida: 18 yosh, Tug'ilgan sana: 11.11.2007, Alfraganus universiteti 1-kurs, Do'stlari: Asad va Javohir, Sinfdoshlari: Juda kop."},
                *chat_histories[user_id]
            ]
        )
        reply = response.choices[0].message.content
        chat_histories[user_id].append({
            "role": "assistant",
            "content": reply
        })
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {str(e)}")

print("Bot ishga tushdi! ✅")
bot.polling(none_stop=True)
