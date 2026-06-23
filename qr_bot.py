#!/usr/bin/env python3
"""
Telegram QR Code Bot — Active QR List
======================================
Reads ONLY the `active_qr_list` table from attendance.db.
When a user sends a recognised emp_id, the bot returns a QR code
encoding that emp_id for scanning at the Training Attendance Manager.

Setup:
  1. pip install python-telegram-bot qrcode[pil] Pillow
     (or install only what's available; fallback logic included)
  2. Set env var TELEGRAM_BOT_TOKEN=<your bot token>
  3. Start: python3 qr_bot.py

Commands:
  /start       — Welcome message
  /list        — Show all emp_ids currently in active_qr_list
  /qr <emp_id> — Generate a QR code for a specific emp_id
  /count       — How many IDs are in the active list
  Sending a plain emp_id also triggers QR generation.
"""

import sqlite3
import os
import sys
import io
import logging
from datetime import datetime

# --- အောက်က နှစ်ကြောင်းကို အသစ်ထည့်ပေးပါ ---
from dotenv import load_dotenv
load_dotenv() 
# ----------------------------------------

# ── Configuration ──────────────────────────────────────────────
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("qr_bot")

# ── Database ───────────────────────────────────────────────────
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def is_in_active_list(emp_id):
    """Check if emp_id exists in active_qr_list."""
    db = get_db()
    try:
        row = db.execute(
            "SELECT emp_id, name FROM active_qr_list WHERE emp_id = ?",
            (emp_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def list_all_active():
    """Return all entries in active_qr_list."""
    db = get_db()
    try:
        rows = db.execute(
            "SELECT emp_id, name FROM active_qr_list ORDER BY name"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def get_active_count():
    db = get_db()
    try:
        return db.execute("SELECT COUNT(*) AS n FROM active_qr_list").fetchone()["n"]
    finally:
        db.close()


# ── QR Code Generation ──────────────────────────────────────────
def generate_qr_image(emp_id):
    """Generate a QR code image (PNG bytes) encoding the emp_id."""
    try:
        import qrcode
        from qrcode.image.styledpil import StyledPilImage
        from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

        qr = qrcode.QRCode(
            version=None,  # auto
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=12,
            border=2,
        )
        qr.add_data(emp_id)
        qr.make(fit=True)
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            fill_color="black",
            back_color="white",
        )
    except (ImportError, TypeError):
        # Fallback: plain qrcode without styled features
        import qrcode
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=3,
        )
        qr.add_data(emp_id)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# ── Bot Handlers ────────────────────────────────────────────────

async def start(update, context):
    """Send welcome message on /start."""
    count = get_active_count()
    await update.message.reply_text(
        "📋 *Training Attendance — QR Bot*\n\n"
        "I generate QR codes for the active attendee list.\n\n"
        f"Currently *{count}* employee{'s' if count != 1 else ''}"
        " in the active QR list.\n\n"
        "• Send an employee ID to get their QR code\n"
        "• /list — Show all active IDs\n"
        "• /qr <ID> — Generate QR for a specific ID\n"
        "• /count — Count of active IDs\n"
        "• /help — This message",
        parse_mode="Markdown",
    )


async def cmd_list(update, context):
    """List all emp_ids in active_qr_list."""
    rows = list_all_active()
    if not rows:
        await update.message.reply_text("ℹ️ The active QR list is empty.")
        return

    lines = [f"• `{r['emp_id']}` — {r['name'] or '(no name)'}" for r in rows]
    text = f"📋 *Active QR List* ({len(rows)} entries):\n\n" + "\n".join(lines)
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_count(update, context):
    """Show active list count."""
    count = get_active_count()
    await update.message.reply_text(f"📊 *{count}* employee ID{'s' if count != 1 else ''} in the active QR list.", parse_mode="Markdown")


async def cmd_qr(update, context):
    """Generate QR for a requested emp_id (via /qr <ID> or plain text)."""
    # Determine the emp_id from the message
    if update.message.text.startswith("/qr"):
        parts = update.message.text.split(maxsplit=1)
        if len(parts) < 2:
            await update.message.reply_text("Usage: `/qr <emp_id>`", parse_mode="Markdown")
            return
        emp_id = parts[1].strip()
    else:
        emp_id = update.message.text.strip()

    if not emp_id:
        return

    # ── ONLY check active_qr_list ────────────────────────
    entry = is_in_active_list(emp_id)
    if not entry:
        await update.message.reply_text(
            f"❌ *{emp_id}* is not in the active QR list.\n\n"
            "The Admin must add this ID via the frontend first.",
            parse_mode="Markdown",
        )
        logger.info(f"Rejected: {emp_id} not in active_qr_list")
        return

    # ── Generate QR ──────────────────────────────────────
    try:
        qr_image = generate_qr_image(emp_id)
    except ImportError as e:
        await update.message.reply_text(
            "⚠️ QR generation library not installed.\n"
            "Run: `pip install qrcode[pil] Pillow`"
        )
        logger.error(f"QR generation failed: {e}")
        return
    except Exception as e:
        await update.message.reply_text(f"⚠️ Failed to generate QR: {e}")
        logger.error(f"QR generation error: {e}")
        return

    display_name = entry["name"] or emp_id
    caption = f"🆔 *{display_name}*\n📱 Scan this QR at the check-in station."
    await update.message.reply_photo(
        photo=qr_image,
        caption=caption,
        parse_mode="Markdown",
    )
    logger.info(f"QR generated for {emp_id} ({display_name})")


async def help_command(update, context):
    """Alias for /help."""
    await start(update, context)


async def unknown_command(update, context):
    """Handle unknown commands."""
    await update.message.reply_text(
        "Unknown command. Try /start or send an employee ID from the active list."
    )


# ── Main ───────────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        logger.error(
            "TELEGRAM_BOT_TOKEN environment variable not set.\n"
            "Export it:  export TELEGRAM_BOT_TOKEN=12345:abcde..."
        )
        sys.exit(1)

    # Check if python-telegram-bot is installed
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
    except ImportError:
        logger.error(
            "python-telegram-bot not installed.\n"
            "Install:  pip install python-telegram-bot"
        )
        sys.exit(1)

    app_builder = Application.builder().token(BOT_TOKEN)
    application = app_builder.build()

    # ── Register handlers ──────────────────────────────
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", cmd_list))
    application.add_handler(CommandHandler("count", cmd_count))
    application.add_handler(CommandHandler("qr", cmd_qr))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_qr))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    logger.info("🤖 QR Bot starting — polling Telegram...")
    logger.info(f"   Database: {DATABASE}")
    application.run_polling()


if __name__ == "__main__":
    main()
