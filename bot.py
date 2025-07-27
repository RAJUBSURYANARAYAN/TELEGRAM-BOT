import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Replace with your actual BotFather token
TOKEN = "7692916445:AAGsiRMMxZZnkc9bH1dm2cyJhAoRaUGnHGk"
UPLOAD_FOLDER = "uploads"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi Surya! Use /getfile <filename.ext> to retrieve your Course file.")

async def getfile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        filename = context.args[0]
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                await context.bot.send_document(chat_id=update.effective_chat.id, document=f)
        else:
            await update.message.reply_text("❌ File not found.")
    else:
        await update.message.reply_text("⚠️ Usage: /getfile <filename.ext>")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getfile", getfile))

    print("🤖 Telegram bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
