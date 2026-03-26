import json
import time
from telegram import Bot, Update, ChatPermissions
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8266202967:AAFGSWb1tWaK325Qq7OKFdC-8K2p-yyWLis"
bot = Bot(token=TOKEN)

FILE = "data.json"


# ========= DATA HANDLING =========
def load_data():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

data = load_data()


# ========= COMMANDS =========

# ➜ إضافة ميعاد جديد
def addtime(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)

    try:
        open_time = context.args[0]
        close_time = context.args[1]

        if chat_id not in data:
            data[chat_id] = []

        data[chat_id].append({
            "open": open_time,
            "close": close_time
        })

        save_data(data)

        update.message.reply_text("✅ تم إضافة الميعاد")

    except:
        update.message.reply_text("❌ استخدم: /addtime 08:00 10:00")


# ➜ عرض المواعيد
def showtimes(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)

    if chat_id not in data or len(data[chat_id]) == 0:
        update.message.reply_text("❌ مفيش مواعيد")
        return

    msg = "📅 المواعيد:\n"
    for t in data[chat_id]:
        msg += f"- فتح: {t['open']} | قفل: {t['close']}\n"

    update.message.reply_text(msg)


# ➜ مسح المواعيد
def cleartimes(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)

    data[chat_id] = []
    save_data(data)

    update.message.reply_text("🗑 تم مسح كل المواعيد")


# ========= GROUP CONTROL =========
def open_group(chat_id):
    try:
        bot.set_chat_permissions(
            chat_id=chat_id,
            permissions=ChatPermissions(can_send_messages=True)
        )
    except:
        pass

def close_group(chat_id):
    try:
        bot.set_chat_permissions(
            chat_id=chat_id,
            permissions=ChatPermissions(can_send_messages=False)
        )
    except:
        pass


# ========= MAIN LOOP =========
def run():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("addtime", addtime))
    dp.add_handler(CommandHandler("showtimes", showtimes))
    dp.add_handler(CommandHandler("cleartimes", cleartimes))

    updater.start_polling()

    print("Bot is running...")

    while True:
        now = time.strftime("%H:%M")

        for chat_id, times_list in data.items():
            for t in times_list:
                if now == t["open"]:
                    open_group(chat_id)

                if now == t["close"]:
                    close_group(chat_id)

        time.sleep(30)


run()