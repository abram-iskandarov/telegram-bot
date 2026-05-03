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
user_stats = {}

def ai(prompt):
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🌤️ Ob-havo", "🕐 Soat & Sana")
    markup.row("😄 Hazil", "🌐 Tarjima")
    markup.row("💰 Valyuta", "🍽️ Retsept")
    markup.row("💪 Motivatsiya", "🎮 Viktorina")
    markup.row("📰 Yangiliklar", "🧮 Kalkulyator")
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
    user_id = message.chat.id
    if user_id not in user_stats:
        user_stats[user_id] = {"name": message.from_user.first_name, "messages": 0}
    bot.reply_to(message, f"Salom, {message.from_user.first_name}! 👋\nMen Abramning shaxsiy AI botiman!\n\nQuyidagi tugmalardan foydalaning 👇", reply_markup=main_menu())
    if user_id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"🆕 Yangi foydalanuvchi: {message.from_user.first_name} (@{message.from_user.username})")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id == ADMIN_ID:
        bot.reply_to(message, f"📊 Jami foydalanuvchilar: {len(user_stats)} ta")

@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def orqaga(message):
    bot.reply_to(message, "Asosiy menyu 👇", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🕐 Soat & Sana")
def soat(message):
    toshkent = pytz.timezone('Asia/Tashkent')
    vaqt = datetime.now(toshkent).strftime("%H:%M:%S")
    sana = datetime.now(toshkent).strftime("%d.%m.%Y")
    kun = datetime.now(toshkent).strftime("%A")
    kunlar = {"Monday": "Dushanba", "Tuesday": "Seshanba", "Wednesday": "Chorshanba", "Thursday": "Payshanba", "Friday": "Juma", "Saturday": "Shanba", "Sunday": "Yakshanba"}
    bot.reply_to(message, f"🕐 Vaqt: {vaqt}\n📅 Sana: {sana}\n📆 Kun: {kunlar.get(kun, kun)}")

@bot.message_handler(func=lambda m: m.text == "😄 Hazil")
def joke(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, ai("Menga bitta JUDA kulgili, original o'zbek hazili ayt. Qo'shni, do'st, talaba haqida bo'lsin. Bachkana bo'lmasin, juda kulgili bo'lsin!"))

@bot.message_handler(func=lambda m: m.text == "🌤️ Ob-havo")
def havo(message):
    bot.reply_to(message, "🗺️ Qaysi viloyat?", reply_markup=viloyatlar_menu())

@bot.message_handler(func=lambda m: m.text in ["Toshkent", "Samarqand", "Buxoro", "Namangan", "Andijon", "Farg'ona", "Qashqadaryo", "Surxondaryo", "Jizzax", "Sirdaryo", "Xorazm", "Navoiy"])
def havo_viloyat(message):
    try:
        url = f"https://wttr.in/{message.text}?format=3&m"
        r = requests.get(url, timeout=5)
        bot.reply_to(message, f"🌤️ {message.text}:\n{r.text}", reply_markup=viloyatlar_menu())
    except:
        bot.reply_to(message, "❌ Xatolik!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🌐 Tarjima")
def tarjima(message):
    bot.reply_to(message, "✍️ Tarjima qilmoqchi bo'lgan matnni yozing:")
    bot.register_next_step_handler(message, tarjima_text)
def tarjima_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, ai(f"Shu matnni ingliz tiliga tarjima qil: {message.text}"), reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "💰 Valyuta")
def valyuta(message):
    try:
        r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/", timeout=5)
        data = r.json()
        usd = next(x for x in data if x["Ccy"] == "USD")
        eur = next(x for x in data if x["Ccy"] == "EUR")
        rub = next(x for x in data if x["Ccy"] == "RUB")
        gbp = next(x for x in data if x["Ccy"] == "GBP")
        bot.reply_to(message, f"💰 Valyuta kurslari:\n\n🇺🇸 1 USD = {float(usd['Rate']):,.0f} so'm\n🇪🇺 1 EUR = {float(eur['Rate']):,.0f} so'm\n🇷🇺 1 RUB = {float(rub['Rate']):.2f} so'm\n🇬🇧 1 GBP = {float(gbp['Rate']):,.0f} so'm")
    except:
        bot.reply_to(message, "❌ Valyuta ma'lumotini ololmadim!")

@bot.message_handler(func=lambda m: m.text == "🍽️ Retsept")
def retsept(message):
    bot.reply_to(message, "🍽️ Qaysi taom retseptini bilmoqchisiz?")
    bot.register_next_step_handler(message, retsept_text)

def retsept_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, ai(f"{message.text} taomining to'liq retseptini yoz."), reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "💪 Motivatsiya")
def motivatsiya(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, ai("Juda kuchli motivatsion ibora yoki qisqa hikoya ayt. O'zbek tilida, ilhomlantiruvchi bo'lsin!"))

@bot.message_handler(func=lambda m: m.text == "🎮 Viktorina")
def viktorina(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, ai("Qiziqarli viktorina savoli ber. 4 ta variant (A,B,C,D) va to'g'ri javob. O'zbek tilida."))

@bot.message_handler(func=lambda m: m.text == "📰 Yangiliklar")
def yangiliklar(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, ai("O'zbekiston va dunyo bo'yicha 5 ta muhim yangilik haqida qisqacha ma'lumot ber."))

@bot.message_handler(func=lambda m: m.text == "🧮 Kalkulyator")
def kalkulyator(message):
    bot.reply_to(message, "🧮 Masala yozing! Masalan: 25 * 4 + 10")
    bot.register_next_step_handler(message, kalkulyator_hisob)

def kalkulyator_hisob(message):
    try:
        natija = eval(message.text)
        bot.reply_to(message, f"🧮 {message.text} = {natija}", reply_markup=main_menu())
    except:
        bot.reply_to(message, "❌ Noto'g'ri format!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🗑️ Tarixni tozala")
def clear(message):
    chat_histories[message.chat.id] = []
    bot.reply_to(message, "✅ Tozalandi!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "ℹ️ Yordam")
def yordam(message):
    bot.reply_to(message, "🤖 Men Abram Iskandarov yaratgan AI botiman!\nIstalgan savol yozing!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle(message):
    user_id = message.chat.id
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    if user_id not in user_stats:
        user_stats[user_id] = {"name": message.from_user.first_name, "messages": 0}
    user_stats[user_id]["messages"] += 1
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
