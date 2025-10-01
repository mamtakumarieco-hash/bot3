import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from datetime import datetime, time
import asyncio

# ✅ Get token from environment variable (set in Render or your host)
TOKEN = os.environ.get("BOT_TOKEN")

# 🔹 Storage for daily keyword logs
logs = {}

# 🔹 Define the keywords you want to track
KEYWORDS = ["REPORT"]

# Function to track keywords
async def track_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return

    text = update.message.text.lower()
    user = update.message.from_user.full_name
    today = datetime.now().strftime("%Y-%m-%d")

    for keyword in KEYWORDS:
        if keyword in text:
            logs.setdefault(today, {}).setdefault(keyword, set()).add(user)

# Function to send daily summary
async def daily_report(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%Y-%m-%d")
    chat_id = context.job.chat_id
    if today in logs:
        report_lines = [f"📊 Daily  report ({today})"]
        for keyword, users in logs[today].items():
            report_lines.append(f"{keyword} → {', '.join(users)}")
        await context.bot.send_message(chat_id=chat_id, text="\n".join(report_lines))
        del logs[today]  # clear after reporting

# Main entry point
async def main():
    if not TOKEN:
        raise ValueError("❌ BOT_TOKEN not found. Set it in environment variables.")

    app = Application.builder().token(TOKEN).build()

    # Listen to all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_keywords))

    # 🔹 Replace this with your group ID (negative number like -100123456789)
    chat_id = -1003127312955

    # Schedule report every day at 23:59
    app.job_queue.run_daily(daily_report, time=time(1,21 ), chat_id=chat_id)

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

