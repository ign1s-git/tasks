import asyncio
import asyncpg
import logging
import random
from aiogram import Bot, Dispatcher, types, BaseMiddleware, F
from aiogram.filters import CommandStart, Command
from aiogram.types import BotCommand
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class SecretGame(StatesGroup):
    guessing = State()  # для игры "/game"

class AnswerGame(StatesGroup):
    waiting_question = State()  # для игры "/answer"

class HireState(StatesGroup):
    waiting_answer = State()  # для "/necessary"

# ТВОЙ ТОКЕН
TOKEN = "8145224906:AAFhdBs2IKUORkf0YpLTPlckKN8Pw0VeTjQ"

# Данные для подключения к базе
DB_USER = "postgres"
DB_PASSWORD = ""
DB_NAME = "stalcraft_bot"
DB_HOST = "127.0.0.1"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
answers = ["Да", "Нет", "Скорее да", "Скорее нет", "Может быть 😊"]
# Создаем "анкету" состояний
class SecretGame(StatesGroup):
    guessing = State()  # Состояние "гадает"

class HireState(StatesGroup):
    waiting_answer = State()

# --- 1. ТУРНИКЕТ (MIDDLEWARE) ---
class ActivityMiddleware(BaseMiddleware):
    def __init__(self, pool):
        self.pool = pool

    async def __call__(self, handler, event, data):
        if isinstance(event, types.Message) and event.from_user:
            user = event.from_user
            xp_gain = random.randint(1, 5)

            await self.pool.execute("""
                INSERT INTO users (user_id, username, xp, level)
                VALUES ($1, $2, $3, 1)
                ON CONFLICT (user_id) DO UPDATE
                SET xp = users.xp + $3,
                    level = (users.xp + $3) / 100 + 1,
                    username = $2
            """, user.id, user.username, xp_gain)

        return await handler(event, data)

# --- 2. ИГРОВАЯ ЛОГИКА (Ставим её ВЫШЕ всего) ---

# Запуск игры
@dp.message(Command("game"))
async def start_game_handler(message: types.Message, state: FSMContext):
    await state.set_state(SecretGame.guessing)
    await message.answer("ты гей?\n(Подсказка: скажи правду)")

# Победа (слово "да" во время игры)
@dp.message(SecretGame.guessing, F.text.lower() == "да")
async def win_handler(message: types.Message, state: FSMContext):
    await message.answer("🎉 ПОЗДРАВЛЯЮ! Ты ответил честно.\nИгра окончена.")
    await state.clear()  # Выключаем игру

# Неправильный ответ (любое другое слово ВО ВРЕМЯ игры)
@dp.message(SecretGame.guessing)
async def wrong_guess_handler(message: types.Message):
    await message.answer("❌ Такой опции нет. Отвечай 'да'.")

# --- 3. ОБЫЧНЫЕ КОМАНДЫ ---

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Я считаю твой опыт.")

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    text = "🏆 Топ игроков:\n\n"
    rows = await db_pool.fetch("SELECT username, xp FROM users ORDER BY xp DESC LIMIT 10")
    for num, row in enumerate(rows, start=1):
        name = row['username'] or "Аноним"
        xp = row['xp']
        text += f"{num}. {name} — {xp} XP\n"
    await message.answer(text)

@dp.message(Command("answer"))
async def cmd_answer(message: types.Message, state: FSMContext):
    # 1️⃣ Устанавливаем состояние, чтобы бот понял, что сейчас игра
    await state.set_state(SecretGame.guessing)  # или другое состояние для Да/Нет игры

    # 2️⃣ Пишем пользователю инструкцию
    await message.answer("Задай мне вопрос, на который хочешь получить ответ:")

# 3️⃣ Обработчик ответа пользователя в этом состоянии
@dp.message(SecretGame.guessing)
async def yes_no_game(message: types.Message, state: FSMContext):
    # Выбираем случайный ответ
    answer = random.choice(answers)
    await message.answer(answer)

    # Спрашиваем, хочет ли пользователь задать ещё один вопрос
    await message.answer("Хочешь задать ещё один вопрос? Напиши что-нибудь или /answer, чтобы начать заново")


# Команда /necessary — запускает мини-игру
@dp.message(Command("necessary"))
async def start_necessary_handler(message: types.Message, state: FSMContext):
    await state.set_state(HireState.waiting_answer)
    await message.answer("Нанять Азизу на работу?")

# Обработка ответов (без ИИ — статические ответы)
@dp.message(HireState.waiting_answer)
async def necessary_repeat_handler(message: types.Message, state: FSMContext):
    text = message.text.lower()

    if text == "да":
        await message.answer(
            "п<tg-spoiler>рекрасно </tg-spoiler> Хороший мальчик). Азиза нанята!",
            parse_mode="HTML"
        )
        await state.clear()

    elif text == "нет":
        # Статический саркастичный ответ
        ai_reply = "Ох, как же ты меня разочаровал. 'Нет'? В следующий раз подумай дважды, прежде чем ломать мечты Азизы. 😏"
        await message.answer(
            f"<tg-spoiler>пидора ответ)</tg-spoiler>\n{ai_reply}",
            parse_mode="HTML"
        )
        # состояние *не* очищаем — продолжаем игру

    else:
        # Статическая шутка
        ai_reply = "Твой ответ звучит как 'я не знаю, что сказать'. Классика! 😆"
        await message.answer(
            f"❗ Такой опции нет :( Повторите ещё раз!\n\n{ai_reply}",
            parse_mode="HTML"
        )

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    row = await db_pool.fetchrow("SELECT xp, level FROM users WHERE user_id = $1", message.from_user.id)
    if row:
        await message.answer(f"📊 Твоя статистика:\n⭐ Уровень: {row['level']}\n✨ Опыт: {row['xp']}")
    else:
        await message.answer("Ты еще не в базе.")

# --- 4. ПРОСТЫЕ ОТВЕТЫ (Если игра НЕ идет) ---

@dp.message(F.text.lower() == "нет")
async def no_handler(message: types.Message):
    await message.answer("<tg-spoiler>пидора ответ)</tg-spoiler>", parse_mode="HTML")

# @dp.message(F.text.lower() == "да")
# async def yes_handler(message: types.Message):
#     await message.answer("Ты написал 'да'! Лови ответ: п<tg-spoiler>анд</tg-spoiler>а", parse_mode="HTML")

# --- 5. ПЫЛЕСОС (Ловит всё остальное) ---
@dp.message()
async def chat_handler(message: types.Message):
    await message.answer("Сообщение принято! +XP")

# --- 6. MAIN (Только запуск) ---
async def main():
    global db_pool

    try:
        db_pool = await asyncpg.create_pool(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST)
        print("✅ База данных успешно подключена!")
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return

    bot = Bot(token=TOKEN)

    # Подключаем Middleware
    dp.message.middleware.register(ActivityMiddleware(db_pool))

    # Меню команд
    commands_for_bot = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="stats", description="📊 Моя статистика"),
        BotCommand(command="top", description="🏆 Рейтинг игроков"),
        BotCommand(command="game", description="🎮 Игра"),
        BotCommand(command="necessary", description="Важно"),
        BotCommand(command="answer", description="Ответ")
    ]
    try:
        await bot.set_my_commands(commands_for_bot)
        print("✅ Меню команд установлено")
    except Exception as e:
        print(f"⚠️ Ошибка меню: {e}")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())