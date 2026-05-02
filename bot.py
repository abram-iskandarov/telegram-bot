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

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🌤️ Ob-havo", "🕐 Soat & Sana")
    markup.row("😄 Hazil", "🌐 Tarjima")
    markup.row("🗑️ Tarixni tozala", "ℹ️ Yordam")
    return markup

def viloyatlar_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Toshkent", "Samarqand")
    markup.row("Buxoro", "Namangan")
    markup.row("Andijon", "Farg'ona")
    markup.row("Qashqadaryo", "Surxondaryo")
    markup.row("Jizzax", "Sirdaryo")
    markup.row("Xorazm", "Navoiy")
    markup.row("🔙 Orqaga")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! 👋 Men Abramning shaxsiy AI botiman!\nQuyidagi tugmalardan foydalaning:", reply_markup=main_menu())
    if message.chat.id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"🆕 Yangi foydalanuvchi: {message.from_user.first_name} (@{message.from_user.username})")

@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def orqaga(message):
    bot.reply_to(message, "Asosiy menyu:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🕐 Soat & Sana")
def soat(message):
    toshkent = pytz.timezone('Asia/Tashkent')
    vaqt = datetime.now(toshkent).strftime("%H:%M:%S")
    sana = datetime.now(toshkent).strftime("%d.%m.%Y")
    bot.reply_to(message, f"🕐 Vaqt: {vaqt}\n📅 Sana: {sana}")

@bot.message_handler(func=lambda m: m.text == "😄 Hazil")
def joke(message):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Menga bitta juda kulgili, mazmunli o'zbek hazili ayt. Qo'shni, do'st, ota-ona haqida bo'lsin. Bachkana bo'lmasin, lekin juda kulgili bo'lsin!"}]
    )
    bot.reply_to(message, response.choices[0].message.content)

@bot.message_handler(func=lambda m: m.text == "🌤️ Ob-havo")
def havo(message):
    bot.reply_to(message, "Qaysi viloyat?", reply_markup=viloyatlar_menu())

@bot.message_handler(func=lambda m: m.text in ["Toshkent", "Samarqand", "Buxoro", "Namangan", "Andijon", "Farg'ona", "Qashqadaryo", "Surxondaryo", "Jizzax", "Sirdaryo", "Xorazm", "Navoiy"])
def havo_viloyat(message):
    shahar = message.text
    try:
        url = f"https://wttr.in/{shahar}?format=3&m"
        r = requests.get(url)
        bot.reply_to(message, f"🌤️ {r.text}", reply_markup=viloyatlar_menu())
    except:
        bot.reply_to(message, "Ob-havo ma'lumotini ololmadim 😕", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🌐 Tarjima")
def tarjima(message):
    bot.reply_to(message, "Tarjima qilish uchun matnni yozing:")
    bot.register_next_step_handler(message, tarjima_text)

def tarjima_text(message):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"Shu matnni ingliz tiliga tarjima qil: {message.text}"}]
    )
    bot.reply_to(message, response.choices[0].message.content, reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🗑️ Tarixni tozala")
def clear(message):
    chat_histories[message.chat.id] = []
    bot.reply_to(message, "✅ Suhbat tarixi tozalandi!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "ℹ️ Yordam")
def yordam(message):
    bot.reply_to(message, "🤖 Men Abram Iskandarov yaratgan AI botiman!\nIstalgan savol yozing — javob beraman!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle(message):
    user_id = message.chat.id
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append({"role": "user", "content": message.text})
    bot.send_chat_action(user_id, 'typing')
    if user_id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"👤 {message.from_user.first_name}: {message.text}")
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Siz Abram Iskandarov yaratgan shaxsiy AI assistantsiz. Hech qachon boshqa kompaniya yaratgan dema. O'zbek tilida, qisqa va aniq javob ber."},
                *chat_histories[user_id]
            ]
        )
        reply = response.choices[0].message.content
        chat_histories[user_id].append({"role": "assistant", "content": reply})
        bot.reply_to(message, reply, reply_markup=main_menu())
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {str(e)}", reply_markup=main_menu())

print("Bot ishga tushdi! ✅")
bot.polling(none_stop=True)
