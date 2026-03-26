import json
import time
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8266202967:AAFGSWb1tWaK325Qq7OKFdC-8K2p-yyWLis"
bot = Bot(token=TOKEN)

FILE = "data.json"

# تحميل البيانات
def load_data():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# حفظ البيانات
def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

data = load_data()

def settime(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)

    try:
        open_time = context.args[0]
        close_time = context.args[1]

        data[chat_id] = {
            "open": open_time,
            "close": close_time
        }

        save_data(data)

        update.message.reply_text("تمام ✅ تم حفظ المواعيد")

    except:
        update.message.reply_text("اكتب كده: /settime 08:00 10:00")

def open_group(chat_id):
    bot.set_chat_permissions(
        chat_id=chat_id,
        permissions={"can_send_messages": True}
    )

def close_group(chat_id):
    bot.set_chat_permissions(
        chat_id=chat_id,
        permissions={"can_send_messages": False}
    )

def run():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("settime", settime))

    updater.start_polling()

    while True:
        now = time.strftime("%H:%M")

        for chat_id, times in data.items():
            if now == times["open"]:
                open_group(chat_id)

            if now == times["close"]:
                close_group(chat_id)

        time.sleep(30)

run()