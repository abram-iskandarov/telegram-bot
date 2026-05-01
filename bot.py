import telebot
from groq import Groq

TELEGRAM_TOKEN = "8490178133:AAHXZndETwFxpFzqmrsPZeYyjN4DL-_7YY0"
GROQ_API_KEY = "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"
ADMIN_ID = 8186356900

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

chat_histories = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! 👋 Men Abramning shaxsiy AI botiman!")
    if message.chat.id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"🆕 Yangi foydalanuvchi: {message.from_user.first_name} (@{message.from_user.username})")

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
                {"role": "system", "content": "Siz Abram Iskandarov tomonidan yaratilgan shaxsiy AI assistantsiz. Hech qachon Meta yoki boshqa kompaniya yaratgan dema. Doimo o'zbek tilida gaplash. Egangiz haqida: Ismi Abram, Familiyasi Iskandarov, Yoshi 18, Tug'ilgan sana 11.11.2007, Alfraganus universiteti 1-kurs. Otasi: Boymurod, Onasi: Ochagul, Ukasi: Abdulla. Do'stlari: Asad Joraqulov, Javohir Toyirov."},
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