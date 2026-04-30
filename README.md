# File Courier Telegram Bot

A secure, user-isolated file transfer system allowing users to anonymously drop files on a web interface and securely retrieve them on their mobile device via a Telegram Bot.

## Features
- **Anonymous Uploading**: No password or sign-up required on the web.
- **Secure Integration**: Files are isolated to specific users via a unique 6-digit Claim Code.
- **Premium UI**: Beautiful, glassmorphic drag-and-drop web interface.
- **Bot Commands**: `/start`, `/claim`, `/list`, `/getfile`, and `/delete`.

## Prerequisites
- Python 3.8+
- A Telegram Bot Token from [@BotFather](https://core.telegram.org/bots#botfather)

## Setup

1. **Clone the repository** (or copy the files):
   ```bash
   git clone <repository_url>
   cd TELEGRAM-BOT
   ```

2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
   *Required packages: `flask`, `python-telegram-bot`*

3. **Configure the Bot**:
   Open `bot.py` and replace `TOKEN` with your actual Telegram bot token.
   ```python
   TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
   ```

## Running the Application

You need to run two processes simultaneously: the Web App (Flask) and the Telegram Bot.

1. **Start the Web Application**:
   ```bash
   python app.py
   ```
   *The app will run locally at `http://127.0.0.1:5000`.*

2. **Start the Telegram Bot** (in a separate terminal):
   ```bash
   python bot.py
   ```
   *You should see "🤖 Telegram bot is running..."*

## How to Use

1. **Upload on Desktop**: 
   Open `http://127.0.0.1:5000` in your browser. Drag and drop file(s) into the Secure Courier UI and click "Upload & Get Code".
2. **Copy the Code**: 
   You will receive a 6-digit Claim Code (e.g., 839201).
3. **Claim on Mobile**: 
   Open your Telegram Bot on your phone. Send the command: `/claim 839201`.
4. **Manage Files**: 
   The bot will confirm the files are linked to your account. Use `/list` to view your encrypted vault, and `/getfile <filename>` to output the file back to your phone!

## Deployment Notes
- For production, use a WSGI server like `gunicorn` to run the Flask app instead of the built-in development server.
- Ensure `temp_uploads` and `uploads` directories have proper read/write permissions.
- The `bot.db` SQLite database is lightweight and requires no setup; it auto-generates upon running `app.py`.
