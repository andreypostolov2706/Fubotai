from __future__ import annotations

import io
import os
from urllib.parse import urlparse

import aiohttp
from loguru import logger
from telegram import InputFile


def _is_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def _guess_ext_from_content_type(content_type: str) -> str | None:
    content_type = (content_type or "").lower()
    if "image/png" in content_type:
        return "png"
    if "image/jpeg" in content_type or "image/jpg" in content_type:
        return "jpg"
    if "image/webp" in content_type:
        return "webp"
    if "video/mp4" in content_type:
        return "mp4"
    if "video/webm" in content_type:
        return "webm"
    return None


def _guess_ext_from_url(url: str) -> str | None:
    try:
        path = urlparse(url).path
        _, ext = os.path.splitext(path)
        ext = ext.lower().lstrip(".")
        if ext in {"png", "jpg", "jpeg", "webp", "mp4", "webm"}:
            return "jpg" if ext == "jpeg" else ext
    except Exception:
        return None
    return None


def _is_webm_url(url: str) -> bool:
    ext = _guess_ext_from_url(url)
    return ext == "webm"


async def _download_bytes(url: str, *, timeout_s: int = 25, max_bytes: int = 50 * 1024 * 1024) -> tuple[bytes, str | None]:
    timeout = aiohttp.ClientTimeout(total=timeout_s)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, allow_redirects=True) as resp:
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type")
            data = await resp.read()
            if len(data) > max_bytes:
                raise ValueError(f"Downloaded file too large: {len(data)} bytes")
            return data, content_type


async def send_photo_robust(
    bot,
    *,
    chat_id: int,
    photo: str,
    caption: str | None = None,
    reply_markup=None,
    parse_mode: str | None = "HTML",
):
    try:
        return await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    except Exception as e:
        logger.error(f"send_photo failed: {e}; photo={photo}")

    if not isinstance(photo, str) or not _is_url(photo):
        raise

    content, content_type = await _download_bytes(photo)
    ext = _guess_ext_from_content_type(content_type) or _guess_ext_from_url(photo) or "jpg"
    filename = f"image.{ext}"
    try:
        return await bot.send_photo(
            chat_id=chat_id,
            photo=InputFile(io.BytesIO(content), filename=filename),
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    except Exception as e2:
        logger.error(f"send_photo(bytes) failed: {e2}; url={photo}")

    return await bot.send_document(
        chat_id=chat_id,
        document=InputFile(io.BytesIO(content), filename=filename),
        caption=caption,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
    )


async def send_video_robust(
    bot,
    *,
    chat_id: int,
    video: str,
    caption: str | None = None,
    reply_markup=None,
    parse_mode: str | None = "HTML",
    always_document: bool = True,
    force_document_for_webm: bool = True,
):
    if always_document:
        return await send_document_robust(
            bot,
            chat_id=chat_id,
            document=video,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )

    if isinstance(video, str) and _is_url(video) and force_document_for_webm and _is_webm_url(video):
        try:
            return await send_document_robust(
                bot,
                chat_id=chat_id,
                document=video,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
        except Exception as e:
            logger.error(f"send_document(webm url) failed: {e}; url={video}")

    try:
        return await bot.send_video(
            chat_id=chat_id,
            video=video,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    except Exception as e:
        logger.error(f"send_video failed: {e}; video={video}")

    return await send_document_robust(
        bot,
        chat_id=chat_id,
        document=video,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
    )


async def send_document_robust(
    bot,
    *,
    chat_id: int,
    document: str,
    caption: str | None = None,
    reply_markup=None,
    parse_mode: str | None = "HTML",
):
    try:
        return await bot.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    except Exception as e:
        logger.error(f"send_document failed: {e}; document={document}")

    if not isinstance(document, str) or not _is_url(document):
        raise

    content, content_type = await _download_bytes(document)
    ext = _guess_ext_from_content_type(content_type) or _guess_ext_from_url(document) or "bin"
    filename = f"file.{ext}"

    return await bot.send_document(
        chat_id=chat_id,
        document=InputFile(io.BytesIO(content), filename=filename),
        caption=caption,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
    )
