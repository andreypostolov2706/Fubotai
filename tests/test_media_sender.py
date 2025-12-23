import asyncio
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.platform.telegram import media_sender


class FakeBot:
    def __init__(self):
        self.calls = []
        self.fail_send_photo = True
        self.fail_send_video = True
        self.fail_send_document = False

    async def send_photo(self, **kwargs):
        self.calls.append(("send_photo", kwargs))
        if self.fail_send_photo:
            raise Exception("Failed to get http url content")
        return {"ok": True, "type": "photo"}

    async def send_video(self, **kwargs):
        self.calls.append(("send_video", kwargs))
        if self.fail_send_video:
            raise Exception("Failed to get http url content")
        return {"ok": True, "type": "video"}

    async def send_document(self, **kwargs):
        self.calls.append(("send_document", kwargs))
        if self.fail_send_document:
            raise Exception("send_document failed")
        return {"ok": True, "type": "document"}


async def _fake_download_bytes(url: str, *, timeout_s: int = 25, max_bytes: int = 50 * 1024 * 1024):
    if url.endswith(".webm"):
        return b"FAKE_WEBM", "video/webm"
    if url.endswith(".mp4"):
        return b"FAKE_MP4", "video/mp4"
    if url.endswith(".png"):
        return b"FAKE_PNG", "image/png"
    return b"FAKE", "application/octet-stream"


async def test_photo_url_fallback_to_bytes():
    bot = FakeBot()

    orig = media_sender._download_bytes
    media_sender._download_bytes = _fake_download_bytes
    try:
        # first send_photo fails, then bytes send_photo succeeds
        bot.fail_send_photo = True

        async def _send_photo_bytes_ok(**kwargs):
            bot.calls.append(("send_photo", kwargs))
            return {"ok": True, "type": "photo"}

        # after first failure, we want second attempt to succeed
        # easiest: flip the flag after first failure by wrapping
        called = {"n": 0}
        async def send_photo_wrapper(**kwargs):
            bot.calls.append(("send_photo", kwargs))
            called["n"] += 1
            if called["n"] == 1:
                raise Exception("Failed to get http url content")
            return {"ok": True, "type": "photo"}

        bot.send_photo = send_photo_wrapper

        await media_sender.send_photo_robust(
            bot,
            chat_id=1,
            photo="https://example.com/test.png",
            caption="cap",
        )

        assert bot.calls[0][0] == "send_photo"
        assert bot.calls[1][0] == "send_photo"
    finally:
        media_sender._download_bytes = orig


async def test_video_webm_goes_to_document():
    bot = FakeBot()

    orig = media_sender._download_bytes
    media_sender._download_bytes = _fake_download_bytes
    try:
        bot.fail_send_video = False  # should not be called for webm

        await media_sender.send_video_robust(
            bot,
            chat_id=1,
            video="https://example.com/test.webm",
            caption="cap",
        )

        assert bot.calls[0][0] == "send_document"
    finally:
        media_sender._download_bytes = orig


async def test_video_mp4_fallback_to_document_on_error():
    bot = FakeBot()

    orig = media_sender._download_bytes
    media_sender._download_bytes = _fake_download_bytes
    try:
        # send_video_robust now always uses send_document first (max reliability)
        bot.fail_send_video = True
        bot.fail_send_document = False

        await media_sender.send_video_robust(
            bot,
            chat_id=1,
            video="https://example.com/test.mp4",
            caption="cap",
        )

        assert bot.calls[0][0] == "send_document"
    finally:
        media_sender._download_bytes = orig


async def main():
    await test_photo_url_fallback_to_bytes()
    await test_video_webm_goes_to_document()
    await test_video_mp4_fallback_to_document_on_error()
    print("OK")


if __name__ == "__main__":
    asyncio.run(main())
