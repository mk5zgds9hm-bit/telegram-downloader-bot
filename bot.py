import os 
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Салом!\n\n"
        "Instagram, YouTube ёки Pinterest ҳаволасини юборинг.\n"
        "Мен видеони юклаб беришга ҳаракат қиламан."
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith(("http://", "https://")):
        await update.message.reply_text("🔗 Илтимос, тўғри ҳавола юборинг.")
        return

    msg = await update.message.reply_text("⏳ Юкланяпти...")

    filename = f"/tmp/video_{update.message.message_id}.%(ext)s"

    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": filename,
        "noplaylist": True,
        "max_filesize": 50 * 1024 * 1024,
    }

    try:
        def run_download():
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])

        await asyncio.to_thread(run_download)

        files = [
            f for f in os.listdir("/tmp")
            if f.startswith(f"video_{update.message.message_id}.")
        ]

        if not files:
            await msg.edit_text("❌ Видео топилмади.")
            return

        filepath = "/tmp/" + files[0]

        with open(filepath, "rb") as video:
            await update.message.reply_video(video=video)

        os.remove(filepath)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(
            "❌ Видео юкланмади.\n"
            "Бошқа ҳавола билан синаб кўринг."
        )

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN топилмади")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, download)
    )

    print("Bot ишлаяпти...")
    app.run_polling()

if __name__ == "__main__":
    main()
