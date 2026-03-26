import json
import asyncio
from datetime import datetime
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8266202967:AAFGSWb1tWaK325Qq7OKFdC-8K2p-yyWLis"
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

# تحميل البيانات عند التشغيل
data = load_data()

# ========= COMMANDS =========

async def addtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    try:
        open_time = context.args[0]  # format HH:MM
        close_time = context.args[1]

        if chat_id not in data:
            data[chat_id] = []

        data[chat_id].append({
            "open": open_time,
            "close": close_time
        })

        save_data(data)
        await update.message.reply_text(f"✅ تم إضافة الميعاد:\nفتح: {open_time} | قفل: {close_time}")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ استخدام خاطئ! اكتب: /addtime 08:00 10:00")

async def showtimes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if chat_id not in data or not data[chat_id]:
        await update.message.reply_text("❌ مفيش مواعيد مسجلة.")
        return

    msg = "📅 المواعيد الحالية:\n"
    for t in data[chat_id]:
        msg += f"- فتح: {t['open']} | قفل: {t['close']}\n"
    await update.message.reply_text(msg)

async def cleartimes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    data[chat_id] = []
    save_data(data)
    await update.message.reply_text("🗑 تم مسح كل المواعيد لهذا الشات.")

# ========= BACKGROUND CHECK (The Core Logic) =========

async def check_times(context: ContextTypes.DEFAULT_TYPE):
    """دالة بتشتغل كل دقيقة بتشيك على المواعيد"""
    now = datetime.now().strftime("%H:%M")
    
    for chat_id, times_list in data.items():
        for t in times_list:
            try:
                if now == t["open"]:
                    await context.bot.set_chat_permissions(
                        chat_id=chat_id,
                        permissions=ChatPermissions(can_send_messages=True)
                    )
                    # اختياري: إرسال رسالة تنبيه
                    # await context.bot.send_message(chat_id=chat_id, text="🔓 تم فتح المجموعة الآن.")

                if now == t["close"]:
                    await context.bot.set_chat_permissions(
                        chat_id=chat_id,
                        permissions=ChatPermissions(can_send_messages=False)
                    )
                    # await context.bot.send_message(chat_id=chat_id, text="🔒 تم قفل المجموعة الآن.")
            except Exception as e:
                print(f"Error updating permissions for {chat_id}: {e}")

# ========= STARTING THE BOT =========

def main():
    # بناء التطبيق
    application = ApplicationBuilder().token(TOKEN).build()

    # إضافة الأوامر
    application.add_handler(CommandHandler("addtime", addtime))
    application.add_handler(CommandHandler("showtimes", showtimes))
    application.add_handler(CommandHandler("cleartimes", cleartimes))

    # إعداد الـ JobQueue للتحقق من المواعيد كل 30 ثانية
    job_queue = application.job_queue
    job_queue.run_repeating(check_times, interval=30, first=10)

    print("البوت شغال دلوقتي...")
    application.run_polling()

if __name__ == "__main__":
    main()
