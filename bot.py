import asyncio
import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler


TOKEN = os.getenv("8937636550:AAH99izvb7LpJsdg_b0fDlmRuXPNUtpbISo")

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "data.json"
TIMEZONE = ZoneInfo("Europe/Warsaw")

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
    "мандарины": {
        "aliases": ["мандарин", "мандарина", "мандарины"],
        "kcal": 53, "protein": 0.8, "fat": 0.3, "carbs": 13
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


def today_key():
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d")


def load_data():
    global users
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            users = json.load(file)


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=2)


def get_user(user_id):
    user_id = str(user_id)

    if user_id not in users:
        users[user_id] = {
            "target_kcal": 3000,
            "target_protein": 130,
            "target_fat": 80,
            "target_carbs": 430,
            "days": {}
        }

    day = today_key()

    if day not in users[user_id]["days"]:
        users[user_id]["days"][day] = {
            "kcal": 0,
            "protein": 0,
            "fat": 0,
            "carbs": 0,
            "items": []
        }
        save_data()

    return users[user_id]


def get_today_data(user):
    day = today_key()
    return user["days"][day]


def bar(current, target, length=12):
    if target <= 0:
        return "░" * length
    filled = int((current / target) * length)
    filled = max(0, min(filled, length))
    return "█" * filled + "░" * (length - filled)


def stats_text(user, day_data):
    return (
        "📊 ТВОЙ ДЕНЬ\n\n"
        f"🔥 Калории\n{bar(day_data['kcal'], user['target_kcal'])}\n"
        f"{day_data['kcal']:.0f} / {user['target_kcal']:.0f} ккал\n"
        f"Осталось: {user['target_kcal'] - day_data['kcal']:.0f} ккал\n\n"

        f"🥩 Белки\n{bar(day_data['protein'], user['target_protein'])}\n"
        f"{day_data['protein']:.1f} / {user['target_protein']:.1f} г\n"
        f"Осталось: {user['target_protein'] - day_data['protein']:.1f} г\n\n"

        f"🥑 Жиры\n{bar(day_data['fat'], user['target_fat'])}\n"
        f"{day_data['fat']:.1f} / {user['target_fat']:.1f} г\n"
        f"Осталось: {user['target_fat'] - day_data['fat']:.1f} г\n\n"

        f"🍚 Углеводы\n{bar(day_data['carbs'], user['target_carbs'])}\n"
        f"{day_data['carbs']:.1f} / {user['target_carbs']:.1f} г\n"
        f"Осталось: {user['target_carbs'] - day_data['carbs']:.1f} г"
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


def add_product_to_day(day_data, product_name, item, amount):
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

    day_data["kcal"] += kcal
    day_data["protein"] += protein
    day_data["fat"] += fat
    day_data["carbs"] += carbs

    day_data["items"].append({
        "name": product_name,
        "amount": amount_text,
        "kcal": round(kcal, 1),
        "protein": round(protein, 1),
        "fat": round(fat, 1),
        "carbs": round(carbs, 1)
    })

    save_data()

    return kcal, protein, fat, carbs, amount_text


def help_text():
    return (
        "🤖 КОМАНДЫ\n\n"
        "/stats — показать КБЖУ за сегодня\n"
        "/reset — сбросить сегодняшний день\n"
        "/days — список сохранённых дней\n"
        "/day 2026-06-14 — посмотреть конкретный день\n"
        "/products — список продуктов\n\n"

        "⚙️ Нормы:\n"
        "/setkcal 3000 — изменить калории\n"
        "/setprotein 130 — изменить белки\n"
        "/setfat 80 — изменить жиры\n"
        "/setcarbs 430 — изменить углеводы\n\n"

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


def day_report(user, date):
    if date not in user["days"]:
        return "За этот день записей нет."

    d = user["days"][date]

    items_text = ""
    for item in d["items"]:
        items_text += (
            f"• {item['name']} ({item['amount']}) — "
            f"{item['kcal']} ккал, "
            f"Б {item['protein']} г, "
            f"Ж {item['fat']} г, "
            f"У {item['carbs']} г\n"
        )

    if not items_text:
        items_text = "Еды не записано."

    return (
        f"📅 День: {date}\n\n"
        f"🔥 Калории: {d['kcal']:.0f} ккал\n"
        f"🥩 Белки: {d['protein']:.1f} г\n"
        f"🥑 Жиры: {d['fat']:.1f} г\n"
        f"🍚 Углеводы: {d['carbs']:.1f} г\n\n"
        f"🍽 Что ел:\n{items_text}"
    )


def simple_advice(text, user, day_data):
    text = text.lower()

    if "сколько" in text or "осталось" in text:
        return stats_text(user, day_data)

    if "что" in text and ("поесть" in text or "купить" in text):
        return (
            "🍽 Дешево добрать можно так:\n\n"
            "🥩 Белок: творог, яйца, skyr, курица, тунец.\n"
            "🍚 Угли: рис, макароны, хлеб, овсянка, бананы.\n"
            "🥑 Жиры: сыр, орехи, масло, арахис.\n\n"
            "Biedronka дешевле, Żabka удобнее. Как всегда, жизнь выбирает между болью и болью подороже."
        )

    if "бел" in text:
        return f"🥩 Белка осталось: {user['target_protein'] - day_data['protein']:.1f} г. Добей творогом, яйцами, skyr или курицей."

    if "угл" in text:
        return f"🍚 Углеводов осталось: {user['target_carbs'] - day_data['carbs']:.1f} г. Добей рисом, макаронами, хлебом или бананами."

    if "жир" in text:
        return f"🥑 Жиров осталось: {user['target_fat'] - day_data['fat']:.1f} г. Добей сыром, орехами, яйцами или маслом."

    return (
        "Я могу считать еду по названию или по цифрам.\n\n"
        "Примеры:\n"
        "• творог 272\n"
        "• 2 яйца\n"
        "• запеканка\n"
        "• пицца 300\n"
        "• клубника 250\n"
        "• 550 22 26 55\n\n"
        "История:\n"
        "• /days\n"
        "• /day 2026-06-14"
    )


@dp.message()
async def handle(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    day_data = get_today_data(user)
    text = message.text.strip()

    if text == "/start":
        await message.answer("👋 Бот КБЖУ запущен.\n\nНапиши /help.")
        return

    if text == "/help":
        await message.answer(help_text())
        return

    if text == "/stats":
        await message.answer(stats_text(user, day_data))
        return

    if text == "/products":
        product_list = ", ".join(PRODUCTS.keys())
        await message.answer("🍽 Продукты, которые я знаю:\n\n" + product_list)
        return

    if text == "/days":
        days = sorted(user["days"].keys(), reverse=True)

        if not days:
            await message.answer("Пока нет сохранённых дней.")
            return

        await message.answer("📅 Сохранённые дни:\n\n" + "\n".join(days[:30]))
        return

    if text.startswith("/day"):
        parts = text.split()

        if len(parts) < 2:
            await message.answer("Пиши так: /day 2026-06-14")
            return

        date = parts[1]
        await message.answer(day_report(user, date))
        return

    if text == "/reset":
        day = today_key()
        user["days"][day] = {
            "kcal": 0,
            "protein": 0,
            "fat": 0,
            "carbs": 0,
            "items": []
        }
        save_data()
        await message.answer("🧹 Сегодняшний день сброшен.")
        return

    if text.startswith("/setkcal"):
        try:
            user["target_kcal"] = float(text.split()[1])
            save_data()
            await message.answer(f"✅ Калории изменены: {user['target_kcal']:.0f} ккал")
        except:
            await message.answer("Пиши так: /setkcal 3000")
        return

    if text.startswith("/setprotein"):
        try:
            user["target_protein"] = float(text.split()[1])
            save_data()
            await message.answer(f"✅ Белки изменены: {user['target_protein']:.0f} г")
        except:
            await message.answer("Пиши так: /setprotein 130")
        return

    if text.startswith("/setfat"):
        try:
            user["target_fat"] = float(text.split()[1])
            save_data()
            await message.answer(f"✅ Жиры изменены: {user['target_fat']:.0f} г")
        except:
            await message.answer("Пиши так: /setfat 80")
        return

    if text.startswith("/setcarbs"):
        try:
            user["target_carbs"] = float(text.split()[1])
            save_data()
            await message.answer(f"✅ Углеводы изменены: {user['target_carbs']:.0f} г")
        except:
            await message.answer("Пиши так: /setcarbs 430")
        return

    product_name, item = find_product(text)

    if item:
        amount = extract_number(text)
        kcal, protein, fat, carbs, amount_text = add_product_to_day(day_data, product_name, item, amount)

        await message.answer(
            f"✅ Записал: {product_name} ({amount_text})\n\n"
            f"🔥 Калории: {kcal:.0f} ккал\n"
            f"🥩 Белки: {protein:.1f} г\n"
            f"🥑 Жиры: {fat:.1f} г\n"
            f"🍚 Углеводы: {carbs:.1f} г\n\n"
            + stats_text(user, day_data)
        )
        return

    try:
        kcal, protein, fat, carbs = map(float, text.replace(",", ".").split())

        day_data["kcal"] += kcal
        day_data["protein"] += protein
        day_data["fat"] += fat
        day_data["carbs"] += carbs

        day_data["items"].append({
            "name": "ручной ввод",
            "amount": "-",
            "kcal": round(kcal, 1),
            "protein": round(protein, 1),
            "fat": round(fat, 1),
            "carbs": round(carbs, 1)
        })

        save_data()

        await message.answer(
            "✅ Записал вручную:\n\n"
            f"🔥 {kcal:.0f} ккал\n"
            f"🥩 Б: {protein:.1f} г\n"
            f"🥑 Ж: {fat:.1f} г\n"
            f"🍚 У: {carbs:.1f} г\n\n"
            + stats_text(user, day_data)
        )
        return

    except:
        await message.answer(simple_advice(text, user, day_data))


async def remind():
    for user_id, user in users.items():
        day = today_key()

        if day not in user["days"]:
            continue

        day_data = user["days"][day]
        left = user["target_kcal"] - day_data["kcal"]

        if left > 500:
            await bot.send_message(
                int(user_id),
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
    load_data()
    await start_web_server()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(remind, "interval", hours=3)
    scheduler.start()

    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запуск"),
        types.BotCommand(command="help", description="Помощь"),
        types.BotCommand(command="stats", description="КБЖУ за сегодня"),
        types.BotCommand(command="reset", description="Сбросить сегодня"),
        types.BotCommand(command="days", description="Список дней"),
        types.BotCommand(command="day", description="Посмотреть день"),
        types.BotCommand(command="products", description="Список продуктов"),
        types.BotCommand(command="setkcal", description="Изменить калории"),
        types.BotCommand(command="setprotein", description="Изменить белки"),
        types.BotCommand(command="setfat", description="Изменить жиры"),
        types.BotCommand(command="setcarbs", description="Изменить углеводы"),
    ])

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
