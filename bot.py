import os
import sqlite3
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

DB_FILE = "hosting_bot.db"
UPLOAD_DIR = Path("user_files")
UPLOAD_DIR.mkdir(exist_ok=True)


def db():
    return sqlite3.connect(DB_FILE)


def init_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT DEFAULT '',
            banned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            token TEXT NOT NULL,
            file_name TEXT DEFAULT '',
            main_file TEXT DEFAULT '',
            status TEXT DEFAULT 'STOPPED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.commit()
    con.close()


def save_user(user_id, username):
    con = db()
    con.execute("""
        INSERT INTO users(user_id, username)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET username=excluded.username
    """, (user_id, username))
    con.commit()
    con.close()


def banned(user_id):
    con = db()
    row = con.execute(
        "SELECT banned FROM users WHERE user_id=?", (user_id,)
    ).fetchone()
    con.close()
    return bool(row and row[0])


def menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("𝐀𝐃𝐃 𝐁𝐎𝐓", callback_data="ADD"),
            InlineKeyboardButton("𝐌𝐘 𝐁𝐎𝐓𝐒", callback_data="BOTS"),
        ],
        [
            InlineKeyboardButton("𝐌𝐘 𝐅𝐈𝐋𝐄𝐒", callback_data="FILES"),
            InlineKeyboardButton("𝐁𝐎𝐓 𝐈𝐍𝐅𝐎", callback_data="INFO"),
        ],
        [
            InlineKeyboardButton("𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒", callback_data="SETTINGS"),
            InlineKeyboardButton("𝐒𝐔𝐏𝐏𝐎𝐑𝐓", callback_data="SUPPORT"),
        ],
        [
            InlineKeyboardButton("𝐌𝐘 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", callback_data="ACCOUNT")
        ],
    ])


def back():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("𝐁𝐀𝐂𝐊", callback_data="HOME")]
    ])


def admin_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("𝐔𝐒𝐄𝐑𝐒", callback_data="AU"),
            InlineKeyboardButton("𝐁𝐎𝐓𝐒", callback_data="AB"),
        ],
        [
            InlineKeyboardButton("𝐅𝐈𝐋𝐄𝐒", callback_data="AF"),
            InlineKeyboardButton("𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒", callback_data="AS"),
        ],
        [
            InlineKeyboardButton("𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓", callback_data="BR"),
            InlineKeyboardButton("𝐁𝐀𝐍 / 𝐔𝐍𝐁𝐀𝐍", callback_data="BAN"),
        ],
        [
            InlineKeyboardButton("𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓", callback_data="ANN"),
            InlineKeyboardButton("𝐌𝐀𝐈𝐍𝐓𝐄𝐍𝐀𝐍𝐂𝐄", callback_data="MAIN"),
        ],
        [
            InlineKeyboardButton("𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒", callback_data="ASET"),
            InlineKeyboardButton("𝐀𝐂𝐓𝐈𝐕𝐈𝐓𝐘 𝐋𝐎𝐆𝐒", callback_data="LOGS"),
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.username or "")

    if banned(user.id):
        await update.message.reply_text("𝐘𝐎𝐔𝐑 𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐈𝐒 𝐁𝐀𝐍𝐍𝐄𝐃.")
        return

    await update.message.reply_text(
        "𝐑𝐎𝐂𝐊𝐒 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 𝐁𝐎𝐓\n\n"
        "𝐅𝐑𝐄𝐄 𝐓𝐄𝐋𝐄𝐆𝐑𝐀𝐌 𝐁𝐎𝐓 𝐇𝐎𝐒𝐓𝐈𝐍𝐆\n\n"
        "𝐒𝐄𝐋𝐄𝐂𝐓 𝐀𝐍 𝐎𝐏𝐓𝐈𝐎𝐍.",
        reply_markup=menu()
    )


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃.")
        return

    await update.message.reply_text(
        "𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋\n\n𝐒𝐄𝐋𝐄𝐂𝐓 𝐀𝐍 𝐎𝐏𝐓𝐈𝐎𝐍.",
        reply_markup=admin_menu()
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    if banned(uid):
        await q.edit_message_text("𝐘𝐎𝐔𝐑 𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐈𝐒 𝐁𝐀𝐍𝐍𝐄𝐃.")
        return

    if q.data == "HOME":
        await q.edit_message_text(
            "𝐑𝐎𝐂𝐊𝐒 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 𝐁𝐎𝐓\n\n𝐒𝐄𝐋𝐄𝐂𝐓 𝐀𝐍 𝐎𝐏𝐓𝐈𝐎𝐍.",
            reply_markup=menu()
        )
        return

    if q.data == "ADD":
        context.user_data["STEP"] = "NAME"
        await q.edit_message_text(
            "𝐀𝐃𝐃 𝐍𝐄𝐖 𝐁𝐎𝐓\n\n𝐒𝐄𝐍𝐃 𝐘𝐎𝐔𝐑 𝐁𝐎𝐓 𝐍𝐀𝐌𝐄.",
            reply_markup=back()
        )
        return

    if q.data == "BOTS":
        con = db()
        rows = con.execute(
            "SELECT id,name,status FROM bots WHERE user_id=? ORDER BY id DESC",
            (uid,)
        ).fetchall()
        con.close()

        if not rows:
            text = "𝐌𝐘 𝐁𝐎𝐓𝐒\n\n𝐍𝐎 𝐁𝐎𝐓𝐒 𝐀𝐃𝐃𝐄𝐃 𝐘𝐄𝐓."
        else:
            text = "𝐌𝐘 𝐁𝐎𝐓𝐒\n\n" + "\n".join(
                f"𝐁𝐎𝐓 #{i} — {name} — {status}"
                for i, name, status in rows
            )
        await q.edit_message_text(text, reply_markup=back())
        return

    pages = {
        "FILES": "𝐌𝐘 𝐅𝐈𝐋𝐄𝐒\n\n𝐔𝐒𝐄 𝐀𝐃𝐃 𝐁𝐎𝐓 𝐓𝐎 𝐔𝐏𝐋𝐎𝐀𝐃𝐄 𝐘𝐎𝐔𝐑 .𝐏𝐘 𝐎𝐑 .𝐙𝐈𝐏 𝐅𝐈𝐋𝐄.",
        "INFO": "𝐁𝐎𝐓 𝐈𝐍𝐅𝐎\n\n𝐕𝐄𝐑𝐒𝐈𝐎𝐍: 𝟏.𝟎\n𝐓𝐘𝐏𝐄: 𝐅𝐑𝐄𝐄\n𝐒𝐓𝐀𝐓𝐔𝐒: 𝐑𝐄𝐀𝐃𝐘",
        "SETTINGS": "𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒\n\n𝐀𝐔𝐓𝐎 𝐑𝐄𝐒𝐓𝐀𝐑𝐓: 𝐎𝐅𝐅\n𝐍𝐎𝐓𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍𝐒: 𝐎𝐍",
        "SUPPORT": "𝐒𝐔𝐏𝐏𝐎𝐑𝐓\n\n𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐓𝐇𝐄 𝐀𝐃𝐌𝐈𝐍 𝐅𝐎𝐑 𝐇𝐄𝐋𝐏.",
        "ACCOUNT": f"𝐌𝐘 𝐀𝐂𝐂𝐎𝐔𝐍𝐓\n\n𝐔𝐒𝐄𝐑 𝐈𝐃: {uid}\n𝐔𝐒𝐄𝐑𝐍𝐀𝐌𝐄: @{q.from_user.username or '𝐍𝐎𝐍𝐄'}",
    }

    if q.data in pages:
        await q.edit_message_text(pages[q.data], reply_markup=back())
        return

    if q.data in {"AU", "AB", "AF", "AS", "BR", "BAN", "ANN", "MAIN", "ASET", "LOGS"}:
        if uid != ADMIN_ID:
            await q.edit_message_text("𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃.")
            return

        con = db()
        users = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        bots = con.execute("SELECT COUNT(*) FROM bots").fetchone()[0]
        con.close()

        admin_text = {
            "AU": f"𝐔𝐒𝐄𝐑𝐒\n\n𝐓𝐎𝐓𝐀𝐋 𝐔𝐒𝐄𝐑𝐒: {users}",
            "AB": f"𝐁𝐎𝐓𝐒\n\n𝐓𝐎𝐓𝐀𝐋 𝐁𝐎𝐓𝐒: {bots}",
            "AF": "𝐅𝐈𝐋𝐄𝐒\n\n𝐅𝐈𝐋𝐄 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓 𝐑𝐄𝐀𝐃𝐘.",
            "AS": f"𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒\n\n𝐔𝐒𝐄𝐑𝐒: {users}\n𝐁𝐎𝐓𝐒: {bots}",
            "BR": "𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓\n\n𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐌𝐎𝐃𝐔𝐋𝐄 𝐑𝐄𝐀𝐃𝐘.",
            "BAN": "𝐁𝐀𝐍 / 𝐔𝐍𝐁𝐀𝐍\n\n𝐔𝐒𝐄𝐑 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓 𝐌𝐎𝐃𝐔𝐋𝐄 𝐑𝐄𝐀𝐃𝐘.",
            "ANN": "𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓\n\n𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓 𝐌𝐎𝐃𝐔𝐋𝐄 𝐑𝐄𝐀𝐃𝐘.",
            "MAIN": "𝐌𝐀𝐈𝐍𝐓𝐄𝐍𝐀𝐍𝐂𝐄\n\n𝐒𝐓𝐀𝐓𝐔𝐒: 𝐎𝐅𝐅.",
            "ASET": "𝐀𝐃𝐌𝐈𝐍 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒\n\n𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒 𝐌𝐎𝐃𝐔𝐋𝐄 𝐑𝐄𝐀𝐃𝐘.",
            "LOGS": "𝐀𝐂𝐓𝐈𝐕𝐈𝐓𝐘 𝐋𝐎𝐆𝐒\n\n𝐋𝐎𝐆 𝐌𝐎𝐃𝐔𝐋𝐄 𝐑𝐄𝐀𝐃𝐘.",
        }[q.data]

        await q.edit_message_text(
            admin_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("𝐁𝐀𝐂𝐊 𝐓𝐎 𝐀𝐃𝐌𝐈𝐍", callback_data="ADMIN")]
            ])
        )
        return

    if q.data == "ADMIN":
        if uid != ADMIN_ID:
            await q.edit_message_text("𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃.")
            return
        await q.edit_message_text(
            "𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋\n\n𝐒𝐄𝐋𝐄𝐂𝐓 𝐀𝐍 𝐎𝐏𝐓𝐈𝐎𝐍.",
            reply_markup=admin_menu()
        )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("STEP")

    if step == "NAME":
        context.user_data["NAME"] = update.message.text.strip()
        context.user_data["STEP"] = "TOKEN"
        await update.message.reply_text("𝐒𝐄𝐍𝐃 𝐘𝐎𝐔𝐑 𝐁𝐎𝐓 𝐓𝐎𝐊𝐄𝐍.")
        return

    if step == "TOKEN":
        context.user_data["TOKEN"] = update.message.text.strip()
        context.user_data["STEP"] = "FILE"
        await update.message.reply_text("𝐔𝐏𝐋𝐎𝐀𝐃 𝐘𝐎𝐔𝐑 .𝐏𝐘 𝐎𝐑 .𝐙𝐈𝐏 𝐅𝐈𝐋𝐄.")
        return

    await update.message.reply_text(
        "𝐏𝐋𝐄𝐀𝐒𝐄 𝐔𝐒𝐄 𝐓𝐇𝐄 𝐌𝐄𝐍𝐔.",
        reply_markup=menu()
    )


async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("STEP") != "FILE":
        await update.message.reply_text(
            "𝐏𝐋𝐄𝐀𝐒𝐄 𝐒𝐓𝐀𝐑𝐓 𝐓𝐇𝐄 𝐀𝐃𝐃 𝐁𝐎𝐓 𝐏𝐑𝐎𝐂𝐄𝐒𝐒 𝐅𝐈𝐑𝐒𝐓."
        )
        return

    doc = update.message.document
    name = doc.file_name or "FILE"

    if not (name.lower().endswith(".py") or name.lower().endswith(".zip")):
        await update.message.reply_text(
            "𝐎𝐍𝐋𝐘 .𝐏𝐘 𝐀𝐍𝐃 .𝐙𝐈𝐏 𝐅𝐈𝐋𝐄𝐒 𝐀𝐑𝐄 𝐀𝐋𝐋𝐎𝐖𝐄𝐃."
        )
        return

    folder = UPLOAD_DIR / str(update.effective_user.id)
    folder.mkdir(parents=True, exist_ok=True)

    tg_file = await doc.get_file()
    await tg_file.download_to_drive(custom_path=str(folder / name))

    con = db()
    con.execute("""
        INSERT INTO bots(user_id,name,token,file_name,status)
        VALUES (?,?,?,?,?)
    """, (
        update.effective_user.id,
        context.user_data.get("NAME", "𝐔𝐍𝐍𝐀𝐌𝐄𝐃"),
        context.user_data.get("TOKEN", ""),
        name,
        "STOPPED"
    ))
    con.commit()
    con.close()

    context.user_data.clear()

    await update.message.reply_text(
        "𝐁𝐎𝐓 𝐀𝐃𝐃𝐄𝐃 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋𝐋𝐘.\n\n"
        f"𝐍𝐀𝐌𝐄: {context.user_data.get('NAME', '𝐁𝐎𝐓')}\n"
        f"𝐅𝐈𝐋𝐄: {name}\n"
        "𝐒𝐓𝐀𝐓𝐔𝐒: 𝐒𝐓𝐎𝐏𝐏𝐄𝐃",
        reply_markup=menu()
    )


def main():
    if BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        raise RuntimeError("PLEASE SET BOT_TOKEN BEFORE STARTING.")

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("ROCKS HOSTING BOT STARTED.")
    app.run_polling()


if __name__ == "__main__":
    main()
