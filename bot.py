import asyncio, json
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

TOKEN = "ВСТАВЬ_ТОКЕН"
URL = "https://ТВОЙ_НИК.github.io/shop/" # Не забудь поменять ссылку
ADMIN_ID = 123456789  # Твой ID для получения заказов

bot = Bot(TOKEN)
dp = Dispatcher()

# База загружается один раз при старте
with open("products.json", encoding="utf-8") as f:
    PRODUCTS = json.load(f)

@dp.message(CommandStart())
async def start(m: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🛍 Открыть каталог", web_app=WebAppInfo(url=URL))]],
        resize_keyboard=True)
    await m.answer("Нажми кнопку ниже, чтобы открыть каталог", reply_markup=kb)

@dp.message(F.web_app_data)
async def order(m: Message):
    # Защита от падения бота при некорректных данных
    try:
        data = json.loads(m.web_app_data.data)
        items = data.get("i", [])
    except (json.JSONDecodeError, AttributeError):
        return await m.answer("❌ Произошла ошибка при обработке данных. Пожалуйста, попробуйте еще раз.")

    lines, total = [], 0
    # items содержит списки вида [id_товара, количество]
    for item in items:
        try:
            pid, qty = item[0], int(item[1])
        except (IndexError, TypeError, ValueError):
            continue
        p = PRODUCTS.get(str(pid))

        # Защита от подмены кол-ва или несуществующих товаров
        if not p or not (0 < qty <= 100):
            continue

        s = p["price"] * qty
        total += s
        lines.append(f"• {p['name']} × {qty} = {s} ₽")

    if not lines:
        return await m.answer("Ваш заказ пуст.")

    text = "\n".join(lines) + f"\n\nИтого: {total} ₽"
    await m.answer("✅ Спасибо, заказ принят! Мы свяжемся с вами в ближайшее время.\n\n" + text)

    # Отправка уведомления администратору
    who = f"@{m.from_user.username}" if m.from_user.username else f"id {m.from_user.id}"
    await bot.send_message(ADMIN_ID, f"🛒 Новый заказ от {who}:\n\n{text}")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
