import os
from aiohttp import web
import asyncio
import re
from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

users = {}

PRODUCTS = {
    "запеканка": {
        "aliases": ["запеканка", "запеканку", "запеканки", "запиканка", "запиканку", "zapiekanka"],
        "kcal": 550, "protein": 22, "fat": 26, "carbs": 55,
        "portion": True
    },
    "яйцо": {
        "aliases": ["яйцо", "яйца", "яиц", "яичко", "яички", "jajko", "jajka"],
        "kcal": 70, "protein": 6, "fat": 5, "carbs": 0.5,
        "piece": True
    },
    "банан": {
        "aliases": ["банан", "банана", "бананы", "бананов", "banan", "banany"],
        "kcal": 89, "protein": 1.1, "fat": 0.3, "carbs": 23
    },
    "яблоко": {
        "aliases": ["яблоко", "яблока", "яблоки", "яблок", "apple", "jabłko"],
        "kcal": 52, "protein": 0.3, "fat": 0.2, "carbs": 14
    },
    "клубника": {
        "aliases": ["клубника", "клубнику", "клубники", "truskawka", "truskawki"],
        "kcal": 32, "protein": 0.7, "fat": 0.3, "carbs": 7.7
    },
    "виноград": {
        "aliases": ["виноград", "винограда"],
        "kcal": 69, "protein": 0.7, "fat": 0.2, "carbs": 18
    },
    "груша": {
        "aliases": ["груша", "грушу", "груши"],
        "kcal": 57, "protein": 0.4, "fat": 0.1, "carbs": 15
    },
    "апельсин": {
        "aliases": ["апельсин", "апельсина", "апельсины"],
        "kcal": 47, "protein": 0.9, "fat": 0.1, "carbs": 12
    },
    "рис": {
        "aliases": ["рис", "риса", "ryż"],
        "kcal": 344, "protein": 6.7, "fat": 0.7, "carbs": 78
    },
    "макароны": {
        "aliases": ["макароны", "макарон", "паста", "спагетти", "spaghetti", "makaron"],
        "kcal": 350, "protein": 12, "fat": 1.5, "carbs": 72
    },
    "гречка": {
        "aliases": ["гречка", "гречку", "гречки", "kasza"],
        "kcal": 343, "protein": 13, "fat": 3.4, "carbs": 72
    },
    "овсянка": {
        "aliases": ["овсянка", "овсянку", "овсяные", "owsianka", "płatki"],
        "kcal": 370, "protein": 13, "fat": 7, "carbs": 60
    },
    "хлеб": {
        "aliases": ["хлеб", "хлеба", "chleb"],
        "kcal": 250, "protein": 8, "fat": 3, "carbs": 49
    },
    "булка": {
        "aliases": ["булка", "булку", "булки", "булочка", "булочку", "bułka", "bułki"],
        "kcal": 300, "protein": 8, "fat": 6, "carbs": 55
    },
    "картошка": {
        "aliases": ["картошка", "картошку", "картофель", "ziemniaki"],
        "kcal": 77, "protein": 2, "fat": 0.1, "carbs": 17
    },
    "творог": {
        "aliases": ["творог", "творога", "творожок", "twaróg"],
        "kcal": 151, "protein": 17, "fat": 8, "carbs": 2.7
    },
    "сыр": {
        "aliases": ["сыр", "сыра", "ser"],
        "kcal": 350, "protein": 25, "fat": 27, "carbs": 2
    },
    "молоко": {
        "aliases": ["молоко", "молока", "mleko"],
        "kcal": 60, "protein": 3.2, "fat": 3.2, "carbs": 4.8
    },
    "йогурт": {
        "aliases": ["йогурт", "йогурта", "йогурты", "jogurt"],
        "kcal": 90, "protein": 4, "fat": 3, "carbs": 12
    },
    "skyr": {
        "aliases": ["skyr", "скир", "скирчик"],
        "kcal": 65, "protein": 12, "fat": 0.2, "carbs": 4
    },
    "курица": {
        "aliases": ["курица", "курицу", "куриное", "куриная", "курицы", "kurczak"],
        "kcal": 165, "protein": 31, "fat": 3.6, "carbs": 0
    },
    "тунец": {
        "aliases": ["тунец", "тунца", "tuńczyk"],
        "kcal": 116, "protein": 26, "fat": 1, "carbs": 0
    },
    "сосиска": {
        "aliases": ["сосиска", "сосиску", "сосиски", "parówka"],
        "kcal": 260, "protein": 12, "fat": 22, "carbs": 3
    },
    "колбаса": {
        "aliases": ["колбаса", "колбасу", "колбасы", "салями", "пепперони", "kiełbasa"],
        "kcal": 320, "protein": 16, "fat": 28, "carbs": 2
    },
    "пицца": {
        "aliases": ["пицца", "пиццу", "пиццы", "pizza"],
        "kcal": 266, "protein": 11, "fat": 10, "carbs": 33
    },
    "хотдог": {
        "aliases": ["хотдог", "хот-дог", "hotdog", "hot-dog"],
        "kcal": 350, "protein": 12, "fat": 20, "carbs": 32,
        "portion": True
    },
    "сэндвич": {
        "aliases": ["сэндвич", "сендвич", "sandwich", "kanapka"],
        "kcal": 400, "protein": 18, "fat": 18, "carbs": 42,
        "portion": True
    },
    "шоколад": {
        "aliases": ["шоколад", "шоколадка", "шоколадку", "czekolada"],
        "kcal": 550, "protein": 7, "fat": 35, "carbs": 55
    },
    "орехи": {
        "aliases": ["орехи", "орехов", "nuts", "orzechy"],
        "kcal": 600, "protein": 20, "fat": 50, "carbs": 20
    },
    "арахис": {
        "aliases": ["арахис", "арахиса"],
        "kcal": 567, "protein": 26, "fat": 49, "carbs": 16
    },
    "масло": {
        "aliases": ["масло", "масла", "butter", "masło"],
        "kcal": 748, "protein": 0.5, "fat": 82, "carbs": 0.8
    },
    "нутелла": {
        "aliases": ["нутелла", "nutella"],
        "kcal": 540, "protein": 6, "fat": 31, "carbs": 57
    }
}


def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "target_kcal": 3000,
            "target_protein": 130,
            "target_fat": 80,
            "target_carbs": 430,
            "kcal": 0,
            "protein": 0,
            "fat": 0,
            "carbs": 0
        }
    return users[user_id]


def bar(current, target, length=12):
    if target <= 0:
        return "░" * length
    filled = int((current / target) * length)
    filled = max(0, min(filled, length))
    return "█" * filled + "░" * (length - filled)


def stats_text(data):
    return (
        "📊 ТВОЙ ДЕНЬ\n\n"
        f"🔥 Калории\n{bar(data['kcal'], data['target_kcal'])}\n"
        f"{data['kcal']:.0f} / {data['target_kcal']:.0f} ккал\n"
        f"Осталось: {data['target_kcal'] - data['kcal']:.0f} ккал\n\n"

        f"🥩 Белки\n{bar(data['protein'], data['target_protein'])}\n"
        f"{data['protein']:.1f} / {data['target_protein']:.1f} г\n"
        f"Осталось: {data['target_protein'] - data['protein']:.1f} г\n\n"

        f"🥑 Жиры\n{bar(data['fat'], data['target_fat'])}\n"
        f"{data['fat']:.1f} / {data['target_fat']:.1f} г\n"
        f"Осталось: {data['target_fat'] - data['fat']:.1f} г\n\n"

        f"🍚 Углеводы\n{bar(data['carbs'], data['target_carbs'])}\n"
        f"{data['carbs']:.1f} / {data['target_carbs']:.1f} г\n"
        f"Осталось: {data['target_carbs'] - data['carbs']:.1f} г"
    )


def find_product(text):
    text = text.lower()
    for name, item in PRODUCTS.items():
        for alias in item["aliases"]:
            if re.search(rf"\b{re.escape(alias.lower())}\b", text):
                return name, item
    return None, None


def extract_number(text):
    text = text.replace(",", ".")
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if not nums:
        return None
    return float(nums[0])


def add_product_to_data(data, product_name, item, amount):
    if item.get("piece"):
        if amount is None:
            amount = 1
        multiplier = amount
        amount_text = f"{amount:.0f} шт."

    elif item.get("portion"):
        if amount is None:
            amount = 1
        multiplier = amount
        amount_text = f"{amount:.0f} порц."

    else:
        if amount is None:
            amount = 100
        multiplier = amount / 100
        amount_text = f"{amount:.0f} г"

    kcal = item["kcal"] * multiplier
    protein = item["protein"] * multiplier
    fat = item["fat"] * multiplier
    carbs = item["carbs"] * multiplier

    data["kcal"] += kcal
    data["protein"] += protein
    data["fat"] += fat
    data["carbs"] += carbs

    return kcal, protein, fat, carbs, amount_text


def help_text():
    return (
        "🤖 КОМАНДЫ\n\n"
        "/stats — показать КБЖУ\n"
        "/reset — сбросить день\n"
        "/setkcal 3000 — изменить калории\n"
        "/setprotein 130 — изменить белки\n"
        "/setfat 80 — изменить жиры\n"
        "/setcarbs 430 — изменить углеводы\n"
        "/products — список продуктов\n\n"

        "🍽 Как добавлять еду:\n"
        "• 550 22 26 55\n"
        "• творог 272\n"
        "• 2 яйца\n"
        "• запеканка\n"
        "• пицца 300\n"
        "• клубника 250\n\n"

        "Для обычных продуктов число = граммы.\n"
        "Для яиц число = штуки.\n"
        "Для запеканки/хотдога/сэндвича число = порции."
    )


def simple_advice(text, data):
    text = text.lower()

    if "сколько" in text or "осталось" in text:
        return stats_text(data)

    if "что" in text and ("поесть" in text or "купить" in text):
        return (
            "🍽 Дешево добрать можно так:\n\n"
            "🥩 Белок: творог, яйца, skyr, курица, тунец.\n"
            "🍚 Угли: рис, макароны, хлеб, овсянка, бананы.\n"
            "🥑 Жиры: сыр, орехи, масло, арахис.\n\n"
            "Biedronka дешевле, Żabka удобнее. Как всегда, жизнь выбирает между болью и болью подороже."
        )

    if "бел" in text:
        return f"🥩 Белка осталось: {data['target_protein'] - data['protein']:.1f} г. Добей творогом, яйцами, skyr или курицей."

    if "угл" in text:
        return f"🍚 Углеводов осталось: {data['target_carbs'] - data['carbs']:.1f} г. Добей рисом, макаронами, хлебом или бананами."

    if "жир" in text:
        return f"🥑 Жиров осталось: {data['target_fat'] - data['fat']:.1f} г. Добей сыром, орехами, яйцами или маслом."

    return (
        "Я могу считать еду по названию или по цифрам.\n\n"
        "Примеры:\n"
        "• творог 272\n"
        "• 2 яйца\n"
        "• запеканка\n"
        "• пицца 300\n"
        "• клубника 250\n"
        "• 550 22 26 55"
    )


@dp.message()
async def handle(message: types.Message):
    user_id = message.from_user.id
    data = get_user(user_id)
    text = message.text.strip()

    if text == "/start":
        await message.answer("👋 Бот КБЖУ запущен.\n\nНапиши /help.")
        return

    if text == "/help":
        await message.answer(help_text())
        return

    if text == "/stats":
        await message.answer(stats_text(data))
        return

    if text == "/products":
        product_list = ", ".join(PRODUCTS.keys())
        await message.answer("🍽 Продукты, которые я знаю:\n\n" + product_list)
        return

    if text == "/reset":
        data["kcal"] = 0
        data["protein"] = 0
        data["fat"] = 0
        data["carbs"] = 0
        await message.answer("🧹 День сброшен.")
        return

    if text.startswith("/setkcal"):
        try:
            data["target_kcal"] = float(text.split()[1])
            await message.answer(f"✅ Калории изменены: {data['target_kcal']:.0f} ккал")
        except:
            await message.answer("Пиши так: /setkcal 3000")
        return

    if text.startswith("/setprotein"):
        try:
            data["target_protein"] = float(text.split()[1])
            await message.answer(f"✅ Белки изменены: {data['target_protein']:.0f} г")
        except:
            await message.answer("Пиши так: /setprotein 130")
        return

    if text.startswith("/setfat"):
        try:
            data["target_fat"] = float(text.split()[1])
            await message.answer(f"✅ Жиры изменены: {data['target_fat']:.0f} г")
        except:
            await message.answer("Пиши так: /setfat 80")
        return

    if text.startswith("/setcarbs"):
        try:
            data["target_carbs"] = float(text.split()[1])
            await message.answer(f"✅ Углеводы изменены: {data['target_carbs']:.0f} г")
        except:
            await message.answer("Пиши так: /setcarbs 430")
        return

    product_name, item = find_product(text)

    if item:
        amount = extract_number(text)
        kcal, protein, fat, carbs, amount_text = add_product_to_data(data, product_name, item, amount)

        await message.answer(
            f"✅ Записал: {product_name} ({amount_text})\n\n"
            f"🔥 Калории: {kcal:.0f} ккал\n"
            f"🥩 Белки: {protein:.1f} г\n"
            f"🥑 Жиры: {fat:.1f} г\n"
            f"🍚 Углеводы: {carbs:.1f} г\n\n"
            + stats_text(data)
        )
        return

    try:
        kcal, protein, fat, carbs = map(float, text.replace(",", ".").split())

        data["kcal"] += kcal
        data["protein"] += protein
        data["fat"] += fat
        data["carbs"] += carbs

        await message.answer(
            "✅ Записал вручную:\n\n"
            f"🔥 {kcal:.0f} ккал\n"
            f"🥩 Б: {protein:.1f} г\n"
            f"🥑 Ж: {fat:.1f} г\n"
            f"🍚 У: {carbs:.1f} г\n\n"
            + stats_text(data)
        )
        return

    except:
        await message.answer(simple_advice(text, data))


async def remind():
    for user_id, data in users.items():
        left = data["target_kcal"] - data["kcal"]
        if left > 500:
            await bot.send_message(
                user_id,
                f"⏰ Напоминание\n\n"
                f"Осталось примерно {left:.0f} ккал. Пора поесть."
            )

async def health(request):
    return web.Response(text="Bot is alive")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_web_server()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(remind, "interval", hours=3)
    scheduler.start()

    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запуск"),
        types.BotCommand(command="help", description="Помощь"),
        types.BotCommand(command="stats", description="КБЖУ за день"),
        types.BotCommand(command="reset", description="Сбросить день"),
        types.BotCommand(command="products", description="Список продуктов"),
        types.BotCommand(command="setkcal", description="Изменить калории"),
        types.BotCommand(command="setprotein", description="Изменить белки"),
        types.BotCommand(command="setfat", description="Изменить жиры"),
        types.BotCommand(command="setcarbs", description="Изменить углеводы"),
    ])

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())