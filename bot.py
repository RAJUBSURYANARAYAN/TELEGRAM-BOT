import os
import shutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.request import HTTPXRequest
from database import get_and_delete_code

# Replace with your actual BotFather token
TOKEN = "7692916445:AAF0z9dsNXEVhP5V5e1l3pQqIeP_MqW5eMs"
TEMP_UPLOAD_FOLDER = "temp_uploads"
UPLOAD_FOLDER = "uploads"

os.makedirs(TEMP_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "👋 Welcome to the File Courier Bot!\n\n"
        "Here's how to use me:\n"
        "1. Open our website and drop your files.\n"
        "2. You'll receive a 6-digit Claim Code.\n"
        "3. Send `/claim <code>` here to securely save your files to your account.\n"
        "4. Use `/list` to see your files.\n"
        "5. Use `/getfile <filename>` to retrieve a file.\n"
        "6. Use `/delete <filename>` to remove a file."
    )
    await update.message.reply_text(welcome_message)

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /claim <code>")
        return

    code = context.args[0]
    folder_uuid = get_and_delete_code(code)

    if not folder_uuid:
        await update.message.reply_text("❌ Invalid or expired claim code.")
        return

    chat_id = str(update.effective_chat.id)
    user_folder = os.path.join(UPLOAD_FOLDER, chat_id)
    os.makedirs(user_folder, exist_ok=True)

    temp_folder = os.path.join(TEMP_UPLOAD_FOLDER, folder_uuid)
    if not os.path.exists(temp_folder):
        await update.message.reply_text("❌ Temporary folder missing. Files may have been lost.")
        return

    # Move files to user's folder
    files_moved = 0
    for filename in os.listdir(temp_folder):
        src = os.path.join(temp_folder, filename)
        dst = os.path.join(user_folder, filename)
        
        # If file already exists, overwrite or handle. For simplicity, we overwrite.
        if os.path.exists(dst):
            os.remove(dst)
            
        shutil.move(src, dst)
        files_moved += 1

    # Cleanup temp folder
    shutil.rmtree(temp_folder)

    await update.message.reply_text(f"✅ Successfully claimed {files_moved} file(s)!\nUse /list to view them.")

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_folder = os.path.join(UPLOAD_FOLDER, chat_id)

    if not os.path.exists(user_folder) or not os.listdir(user_folder):
        await update.message.reply_text("📂 You have no files stored. Upload claiming code first.")
        return

    files = os.listdir(user_folder)
    context.user_data['files'] = files

    keyboard = []
    for i, f in enumerate(files):
        # Truncate long filenames to not overflow buttons
        display_name = f if len(f) < 40 else f[:37] + "..."
        keyboard.append([
            InlineKeyboardButton(f"⬇️ {display_name}", callback_data=f"get_{i}")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📦 Your Files:\nClick a file below to securely download it instantly:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
def get_lan_download_url(chat_id, filename):
    import socket
    from urllib.parse import quote
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = '127.0.0.1'
    safe_filename = quote(filename)
    return f"http://{ip}:5000/download/{chat_id}/{safe_filename}"

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("get_"):
        idx = int(data.split("_")[1])
        files = context.user_data.get('files', [])

        if idx >= len(files):
            await query.message.reply_text("❌ File list expired. Please run /list again.")
            return

        filename = files[idx]
        chat_id = str(query.message.chat.id)
        filepath = os.path.join(UPLOAD_FOLDER, chat_id, filename)

        if os.path.exists(filepath):
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if file_size_mb > 50:
                download_url = get_lan_download_url(chat_id, filename)
                await query.message.reply_text(
                    f"❌ '{filename}' is {file_size_mb:.1f}MB.\n\n"
                    f"Telegram strictly limits bots to 50 MB! "
                    f"Download this giant file locally and securely here:\n\n🔗 {download_url}"
                )
                return
                
            msg = await query.message.reply_text(f"⏳ Uploading {filename}...")
            try:
                with open(filepath, "rb") as f:
                    file_bytes = f.read()
                await context.bot.send_document(chat_id=chat_id, document=file_bytes, filename=filename)
                await msg.delete()
            except Exception as e:
                # SSL malloc failure / NetworkError fallback
                download_url = get_lan_download_url(chat_id, filename)
                try:
                    await msg.delete()
                except:
                    pass
                await query.message.reply_text(
                    f"⚠️ Telegram rejected the upload for '{filename}' (likely due to Python SSL limits).\n\n"
                    f"No worries! You can download it directly here:\n\n🔗 {download_url}"
                )
        else:
            await query.message.reply_text("❌ File not found. You may have deleted it.")

async def getfile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /getfile <filename.ext>")
        return

    filename = " ".join(context.args)
    chat_id = str(update.effective_chat.id)
    
    if "/" in filename or "\\" in filename or ".." in filename:
        await update.message.reply_text("❌ Invalid filename.")
        return

    filepath = os.path.join(UPLOAD_FOLDER, chat_id, filename)

    if os.path.exists(filepath):
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        if file_size_mb > 50:
            download_url = get_lan_download_url(chat_id, filename)
            await update.message.reply_text(
                f"❌ '{filename}' is {file_size_mb:.1f}MB.\n\n"
                f"Telegram strictly limits bots to 50 MB! "
                f"Since your phone and PC are likely on the same Wi-Fi, you can download "
                f"the massive file directly at high speed here:\n\n🔗 {download_url}"
            )
            return
            
        msg = await update.message.reply_text("⏳ Uploading file...")
        try:
            with open(filepath, "rb") as f:
                file_bytes = f.read()
            await context.bot.send_document(chat_id=chat_id, document=file_bytes, filename=filename)
            await msg.delete()
        except Exception as e:
            download_url = get_lan_download_url(chat_id, filename)
            try:
                await msg.delete()
            except:
                pass
            await update.message.reply_text(
                f"⚠️ Telegram rejected the upload for '{filename}' (likely due to Python SSL limits).\n\n"
                f"No worries! You can download it directly here:\n\n🔗 {download_url}"
            )
    else:
        await update.message.reply_text("❌ File not found. Make sure you typed the name correctly (check /list).")

async def deletefile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /delete <filename.ext>")
        return

    filename = " ".join(context.args)
    chat_id = str(update.effective_chat.id)
    
    if "/" in filename or "\\" in filename or ".." in filename:
        await update.message.reply_text("❌ Invalid filename.")
        return

    filepath = os.path.join(UPLOAD_FOLDER, chat_id, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
        await update.message.reply_text(f"🗑️ File '{filename}' deleted from your vault.")
    else:
        await update.message.reply_text("❌ File not found.")

def main():
    # Force HTTP/1.1 to fix Python 3.13 / Windows HTTPX SSL bugs
    request = HTTPXRequest(http_version="1.1")
    app = ApplicationBuilder().token(TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("list", list_files))
    app.add_handler(CommandHandler("getfile", getfile))
    app.add_handler(CommandHandler("delete", deletefile))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 Telegram bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
