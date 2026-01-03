# ======================================
#        ESCROW TELEGRAM BOT
#   Single File - Pydroid3 Compatible
# ======================================

import asyncio
import logging
import aiosqlite
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ======================================
#              CONFIG
# ======================================

BOT_TOKEN = "8245593261:AAGEiWnRQtHEouPkxUKg73WeFpcVV2qjH9I"
OWNER_ID = 7244846730
GROUP_ID = -1003354066361
BOT_IS_ADMIN = True
INITIAL_ADMINS = [968594559, 6167469713, 7991551]

MIN_RATING = 1
MAX_RATING = 5

INVITE_LIMIT = 2
REVOKE_INVITE_ON_FINISH = True

ENABLE_LOG = True
LOG_FILE = "bot.log"

DB_NAME = "escrow.db"
SQLITE_WAL = True

LANG = "fa"
DEAL_EXPIRE_MINUTES = 0

WELCOME_TEXT = "خوش آمدید"
DEAL_CREATED_TEXT = "معامله ثبت شد"

# ======================================
#              LOGGING
# ======================================

if ENABLE_LOG:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

# ======================================
#              BOT INIT
# ======================================

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ======================================
#              STATES
# ======================================

class DealState(StatesGroup):
    description = State()
    amount = State()
    counterparty = State()

# ======================================
#              DATABASE
# ======================================

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        if SQLITE_WAL:
            await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT,
            rating_avg REAL DEFAULT 0,
            rating_count INTEGER DEFAULT 0
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS deals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER,
            description TEXT,
            amount TEXT,
            counterparty_id INTEGER,
            status TEXT,
            accepted_by INTEGER,
            invite_link TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS ratings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id INTEGER,
            admin_id INTEGER,
            user_id INTEGER,
            rating INTEGER
        )
        """)
        await db.commit()

async def add_user(user):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users VALUES (?,?,?,?,?)",
            (user.id, user.username or f"id_{user.id}", "owner" if user.id == OWNER_ID else "user", 0, 0)
        )
        await db.commit()

# ======================================
#              KEYBOARDS
# ======================================

def deal_admin_kb(deal_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton("✅ قبول", callback_data=f"accept:{deal_id}"),
        InlineKeyboardButton("❌ رد", callback_data=f"reject:{deal_id}")
    ]])

def finish_kb(deal_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton("🔒 پایان معامله", callback_data=f"finish:{deal_id}")
    ]])

def rating_kb(deal_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(f"⭐{i}", callback_data=f"rate:{deal_id}:{i}") for i in range(MIN_RATING, MAX_RATING+1)
    ]])

def owner_panel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📊 آمار ربات", callback_data="stats")],
        [InlineKeyboardButton("➕ افزودن واسطه", callback_data="add_admin")],
        [InlineKeyboardButton("➖ حذف واسطه", callback_data="remove_admin")]
    ])

# ======================================
#              START
# ======================================

@dp.message(CommandStart())
async def start(message: Message):
    await add_user(message.from_user)
    await message.answer(f"{WELCOME_TEXT}\n\nبرای ایجاد معامله /newdeal را بزنید")

# ======================================
#          CREATE NEW DEAL
# ======================================

@dp.message(F.text == "/newdeal")
async def new_deal(message: Message, state: FSMContext):
    await message.answer("📝 شرح معامله را وارد کنید:")
    await state.set_state(DealState.description)

@dp.message(DealState.description)
async def deal_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("💰 مبلغ واسطه را وارد کنید:")
    await state.set_state(DealState.amount)

@dp.message(DealState.amount)
async def deal_amount(message: Message, state: FSMContext):
    await state.update_data(amount=message.text)
    await message.answer("👤 آیدی طرف مقابل (@username):")
    await state.set_state(DealState.counterparty)

@dp.message(DealState.counterparty)
async def deal_counterparty(message: Message, state: FSMContext):
    username = message.text.replace("@", "")
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT telegram_id FROM users WHERE username=?",
            (username,)
        )
        row = await cur.fetchone()

    if not row:
        await message.answer("❌ طرف مقابل بات را استارت نکرده است.")
        await state.clear()
        return

    data = await state.get_data()
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("""
        INSERT INTO deals
        (creator_id, description, amount, counterparty_id, status)
        VALUES (?,?,?,?,?)
        """, (
            message.from_user.id,
            data["description"],
            data["amount"],
            row[0],
            "pending"
        ))
        deal_id = cur.lastrowid
        await db.commit()

    async with aiosqlite.connect(DB_NAME) as db:
        admins = await (await db.execute(
            "SELECT telegram_id FROM users WHERE role='admin'"
        )).fetchall()

    for admin in admins:
        await bot.send_message(
            admin[0],
            f"📌 معامله جدید\n\n📝 {data['description']}\n💰 {data['amount']}",
            reply_markup=deal_admin_kb(deal_id)
        )

    await message.answer(f"{DEAL_CREATED_TEXT}")
    await state.clear()

# ======================================
#         ADMIN ACCEPT / REJECT
# ======================================

@dp.callback_query(F.data.startswith("accept"))
async def accept_deal(call: CallbackQuery):
    deal_id = int(call.data.split(":")[1])

    async with aiosqlite.connect(DB_NAME) as db:
        deal = await (await db.execute(
            "SELECT * FROM deals WHERE id=?",
            (deal_id,)
        )).fetchone()

        if deal[5] != "pending":
            await call.answer("قبلا بررسی شده")
            return

        invite = await bot.create_chat_invite_link(
            GROUP_ID,
            member_limit=INVITE_LIMIT
        )

        await db.execute("""
        UPDATE deals SET
        status='accepted',
        accepted_by=?,
        invite_link=?
        WHERE id=?
        """, (call.from_user.id, invite.invite_link, deal_id))
        await db.commit()

    await bot.send_message(deal[1], f"🔗 لینک معامله:\n{invite.invite_link}")
    await bot.send_message(deal[4], f"🔗 لینک معامله:\n{invite.invite_link}")

    await call.message.edit_text(
        f"✅ معامله توسط @{call.from_user.username} قبول شد",
        reply_markup=finish_kb(deal_id)
    )

# ======================================
#          FINISH DEAL + RATING
# ======================================

@dp.callback_query(F.data.startswith("finish"))
async def finish_deal(call: CallbackQuery):
    deal_id = int(call.data.split(":")[1])

    async with aiosqlite.connect(DB_NAME) as db:
        deal = await (await db.execute(
            "SELECT * FROM deals WHERE id=?",
            (deal_id,)
        )).fetchone()

        if call.from_user.id != deal[6]:
            await call.answer("⛔ فقط واسطه می‌تواند پایان دهد")
            return

        if REVOKE_INVITE_ON_FINISH:
            await bot.revoke_chat_invite_link(GROUP_ID, deal[7])

        await db.execute(
            "UPDATE deals SET status='finished' WHERE id=?",
            (deal_id,)
        )
        await db.commit()

    for uid in (deal[1], deal[4]):
        await bot.send_message(
            uid,
            "📝 لطفاً به واسطه معامله امتیاز دهید:",
            reply_markup=rating_kb(deal_id)
        )

    await call.message.answer("🔒 معامله پایان یافت")

# ======================================
#              RATING
# ======================================

@dp.callback_query(F.data.startswith("rate"))
async def rate(call: CallbackQuery):
    _, deal_id, rate = call.data.split(":")
    deal_id, rate = int(deal_id), int(rate)

    async with aiosqlite.connect(DB_NAME) as db:
        deal = await (await db.execute(
            "SELECT accepted_by FROM deals WHERE id=?",
            (deal_id,)
        )).fetchone()

        admin_id = deal[0]

        exists = await (await db.execute("""
        SELECT 1 FROM ratings
        WHERE deal_id=? AND user_id=?
        """, (deal_id, call.from_user.id))).fetchone()

        if exists:
            await call.answer("❌ قبلا امتیاز داده‌اید")
            return

        await db.execute("""
        INSERT INTO ratings (deal_id, admin_id, user_id, rating)
        VALUES (?,?,?,?)
        """, (deal_id, admin_id, call.from_user.id, rate))

        await db.execute("""
        UPDATE users SET
        rating_avg = (rating_avg * rating_count + ?) / (rating_count + 1),
        rating_count = rating_count + 1
        WHERE telegram_id=?
        """, (rate, admin_id))

        await db.commit()

    await call.message.edit_text("✅ امتیاز شما ثبت شد، ممنون 🌹")

# ======================================
#              OWNER PANEL
# ======================================

@dp.message(F.text == "/panel")
async def owner_panel(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    await message.answer("👑 پنل مالک", reply_markup=owner_panel_kb())

@dp.callback_query(F.data == "stats")
async def show_stats(call: CallbackQuery):
    async with aiosqlite.connect(DB_NAME) as db:
        users = await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
        deals = await (await db.execute("SELECT COUNT(*) FROM deals")).fetchone()

    await call.message.answer(
        f"👥 کاربران: {users[0]}\n"
        f"📁 معاملات: {deals[0]}"
    )

# ======================================
#                MAIN
# ======================================

async def main():
    await init_db()
    logging.info("Bot Started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())