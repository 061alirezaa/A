# ======================================
# IMPORTS
# ======================================
import asyncio, time, logging, aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ======================================
# CONFIG
# ======================================
BOT_TOKEN = "8245593261:AAGEiWnRQtHEouPkxUKg73WeFpcVV2qjH9I"
OWNER_ID = 7244846730
DB_NAME = "escrow.db"
SPAM_DELAY = 2  # seconds

# ======================================
# BOT INIT
# ======================================
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ======================================
# STATES
# ======================================
class DealState(StatesGroup):
    description = State()
    amount = State()
    counterparty = State()

# ======================================
# DATABASE INIT
# ======================================
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT DEFAULT 'user',
            language TEXT DEFAULT 'fa',
            rating_avg REAL DEFAULT 0,
            rating_count INTEGER DEFAULT 0,
            last_message INTEGER DEFAULT 0
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS deals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER,
            description TEXT,
            amount TEXT,
            counterparty_id INTEGER,
            status TEXT,
            accepted_by INTEGER,
            admin_message_id INTEGER DEFAULT NULL
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS ratings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id INTEGER,
            admin_id INTEGER,
            user_id INTEGER,
            rating INTEGER
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        await db.execute("INSERT OR IGNORE INTO settings VALUES ('force_join','off')")
        await db.execute("INSERT OR IGNORE INTO settings VALUES ('force_join_chat','')")
        await db.commit()

# ======================================
# USER HELPERS
# ======================================
async def add_or_update_user(user):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO users (telegram_id, username)
        VALUES (?, ?)
        ON CONFLICT(telegram_id)
        DO UPDATE SET username=excluded.username
        """, (user.id, user.username or f"id_{user.id}"))
        await db.commit()

async def anti_spam(user_id):
    now = int(time.time())
    async with aiosqlite.connect(DB_NAME) as db:
        row = await (await db.execute("SELECT last_message FROM users WHERE telegram_id=?", (user_id,))).fetchone()
        if row and now - row[0] < SPAM_DELAY:
            return False
        await db.execute("UPDATE users SET last_message=? WHERE telegram_id=?", (now, user_id))
        await db.commit()
    return True

# ======================================
# FORCE JOIN
# ======================================
async def check_force_join(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        row = await (await db.execute("SELECT value FROM settings WHERE key='force_join'")).fetchone()
        if not row or row[0] != "on":
            return True
        chat_row = await (await db.execute("SELECT value FROM settings WHERE key='force_join_chat'")).fetchone()
        chat_id = chat_row[0]
    try:
        from aiogram.methods import GetChatMember
        member = await bot.get_chat_member(chat_id=int(chat_id), user_id=user_id)
        return member.status != "left"
    except:
        return False

# ======================================
# LANG
# ======================================
TEXT = {
    "fa": {"welcome":"👋 خوش آمدید","deal":"📁 ایجاد معامله","admins":"👑 لیست مدیران","stats":"📊 آمار",
           "join_active":"✅ جوین اجباری فعال","join_off":"❌ جوین اجباری غیرفعال"},
    "en": {"welcome":"👋 Welcome","deal":"📁 Create Deal","admins":"👑 Admins","stats":"📊 Stats",
           "join_active":"✅ Force join active","join_off":"❌ Force join off"}
}

# ======================================
# KEYBOARDS
# ======================================
def main_kb(lang):
    t = TEXT[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["deal"], callback_data="new_deal")],
        [InlineKeyboardButton(text=t["admins"], callback_data="list_admins")],
        [InlineKeyboardButton(text="🌐 Change Language", callback_data="change_lang")]
    ])

def lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang_fa")],
        [InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")]
    ])

def owner_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 آمار", callback_data="stats")],
        [InlineKeyboardButton(text="🌐 تغییر وضعیت Join اجباری", callback_data="toggle_join")],
        [InlineKeyboardButton(text="✏️ تغییر کانال Join", callback_data="change_join_channel")]
    ])

def deal_admin_kb(deal_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ قبول", callback_data=f"accept:{deal_id}"),
        InlineKeyboardButton(text="❌ رد", callback_data=f"reject:{deal_id}"),
        InlineKeyboardButton(text="🔒 پایان معامله", callback_data=f"finish:{deal_id}")
    ]])

# ======================================
# START
# ======================================
@dp.message(CommandStart())
async def start(message: Message):
    await add_or_update_user(message.from_user)
    allowed = await check_force_join(message.from_user.id)
    if not allowed:
        await message.answer("⚠ لطفاً ابتدا عضو کانال تعیین شده شوید!")
        return
    async with aiosqlite.connect(DB_NAME) as db:
        lang_row = await (await db.execute("SELECT language FROM users WHERE telegram_id=?", (message.from_user.id,))).fetchone()
        lang = lang_row[0]
    await message.answer(TEXT[lang]["welcome"], reply_markup=main_kb(lang))

# ======================================
# LANGUAGE
# ======================================
@dp.callback_query(F.data == "change_lang")
async def change_lang(call: CallbackQuery):
    await call.message.answer("Select language:", reply_markup=lang_kb())

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET language=? WHERE telegram_id=?", (lang, call.from_user.id))
        await db.commit()
    await call.message.answer("✅ Language updated")

# ======================================
# ADMINS
# ======================================
@dp.callback_query(F.data == "list_admins")
async def list_admins(call: CallbackQuery):
    async with aiosqlite.connect(DB_NAME) as db:
        admins = await (await db.execute("SELECT username FROM users WHERE role='admin'")).fetchall()
    text = "👑 Admins:\n\n" + "\n".join([f"{i+1}- @{a[0]}" for i,a in enumerate(admins)])
    await call.message.answer(text)

# ======================================
# OWNER PANEL
# ======================================
@dp.message(F.text == "/panel")
async def panel(message: Message):
    if message.from_user.id == OWNER_ID:
        async with aiosqlite.connect(DB_NAME) as db:
            row = await (await db.execute("SELECT value FROM settings WHERE key='force_join'")).fetchone()
            join_status = "on" if row[0]=="on" else "off"
        await message.answer(f"👑 Owner Panel\nJoin اجباری: {join_status}", reply_markup=owner_kb())

# Toggle join اجباری
@dp.callback_query(F.data == "toggle_join")
async def toggle_join(call: CallbackQuery):
    async with aiosqlite.connect(DB_NAME) as db:
        row = await (await db.execute("SELECT value FROM settings WHERE key='force_join'")).fetchone()
        new_val = "off" if row[0] == "on" else "on"
        await db.execute("UPDATE settings SET value=? WHERE key='force_join'", (new_val,))
        await db.commit()
    await call.message.answer(f"✅ وضعیت Join اجباری تغییر کرد: {new_val.upper()}")

# تغییر کانال join
@dp.callback_query(F.data == "change_join_channel")
async def change_join_channel(call: CallbackQuery):
    await call.message.answer("لطفاً آیدی یا یوزرنیم کانال را ارسال کنید:")
    await dp.current_state(user=call.from_user.id).set_state(State())  # generic state

@dp.message(State())
async def set_join_channel(message: Message, state: FSMContext):
    chat_id = message.text
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE settings SET value=? WHERE key='force_join_chat'", (chat_id,))
        await db.commit()
    await message.answer(f"✅ کانال Join به {chat_id} تغییر یافت")
    await state.clear()

# ======================================
# CREATE NEW DEAL
# ======================================
@dp.callback_query(F.data == "new_deal")
async def new_deal(call: CallbackQuery, state: FSMContext):
    allowed = await check_force_join(call.from_user.id)
    if not allowed:
        await call.message.answer("⚠ لطفاً ابتدا عضو کانال تعیین شده شوید!")
        return
    await call.message.answer("📝 شرح معامله را وارد کنید:")
    await state.set_state(DealState.description)

@dp.message(DealState.description)
async def deal_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("💰 مبلغ معامله را وارد کنید:")
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
        row = await (await db.execute("SELECT telegram_id FROM users WHERE username=?", (username,))).fetchone()
    if not row:
        await message.answer("❌ طرف مقابل بات را استارت نکرده است.")
        await state.clear()
        return

    data = await state.get_data()
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("""
        INSERT INTO deals (creator_id, description, amount, counterparty_id, status)
        VALUES (?,?,?,?,?)
        """, (message.from_user.id, data["description"], data["amount"], row[0], "pending"))
        deal_id = cur.lastrowid
        await db.commit()

        admins = await (await db.execute("SELECT telegram_id FROM users WHERE role='admin'")).fetchall()
        for admin in admins:
            msg = await bot.send_message(admin[0],
                f"📌 معامله جدید\n\n📝 {data['description']}\n💰 {data['amount']}",
                reply_markup=deal_admin_kb(deal_id)
            )
            await db.execute("UPDATE deals SET admin_message_id=? WHERE id=?", (msg.message_id, deal_id))
        await db.commit()

    await message.answer("✅ معامله ثبت شد")
    await state.clear()

# ======================================
# FINISH DEAL
# ======================================
@dp.callback_query(F.data.startswith("finish"))
async def finish_deal(call: CallbackQuery):
    deal_id = int(call.data.split(":")[1])
    async with aiosqlite.connect(DB_NAME) as db:
        deal = await (await db.execute("SELECT * FROM deals WHERE id=?", (deal_id,))).fetchone()
        if call.from_user.id != deal[6]:
            await call.answer("⛔ فقط واسطه می‌تواند پایان دهد")
            return

        if deal[8]:
            admins = await (await db.execute("SELECT telegram_id FROM users WHERE role='admin'")).fetchall()
            for admin in admins:
                try:
                    await bot.edit_message_text(
                        chat_id=admin[0],
                        message_id=deal[8],
                        text="✅ معامله پایان یافت"
                    )
                except:
                    pass

    await call.message.answer("🔒 معامله پایان یافت")

# ======================================
# MAIN
# ======================================
async def main():
    await init_db()
    logging.info("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())