from telegram import Update
from telegram.ext import ContextTypes

from core.platform.telegram.media_sender import send_photo_robust, send_video_robust


TEST_IMAGE_URL = "https://picsum.photos/seed/fubotai/900/600.jpg"
TEST_VIDEO_URL = "https://filesamples.com/samples/video/mp4/sample_640x360.mp4"


async def test_media_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    await context.bot.send_message(
        chat_id=chat_id,
        text="🧪 Тест медиа: отправляю картинку и видео (видео как файл/document), без FAL.",
    )

    await send_photo_robust(
        context.bot,
        chat_id=chat_id,
        photo=TEST_IMAGE_URL,
        caption="🧪 Test image",
    )

    await send_video_robust(
        context.bot,
        chat_id=chat_id,
        video=TEST_VIDEO_URL,
        caption="🧪 Test video (sent as document for reliability)",
    )

    await context.bot.send_message(chat_id=chat_id, text="✅ Тест медиа завершён")
