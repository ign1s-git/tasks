import asyncio
import asyncpg

# НАСТРОЙКИ
# В приложении Postgres.app пароль обычно не нужен, поэтому оставляем пустым
# Имя пользователя 'postgres' создается по умолчанию при нажатии Initialize
DB_USER = "postgres"
DB_PASSWORD = ""
DB_HOST = "127.0.0.1"

async def create_db_structure():
    print("⏳ Начинаю настройку базы данных...")

    # ШАГ 1. Создаем саму базу данных
    try:
        # Подключаемся к системной базе 'template1', чтобы создать новую
        conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database='template1')

        try:
            # Пытаемся создать базу (если она уже есть, код пойдет дальше)
            await conn.execute('CREATE DATABASE stalcraft_bot')
            print("✅ База данных 'stalcraft_bot' успешно создана!")
        except asyncpg.DuplicateDatabaseError:
            print("ℹ️ База данных 'stalcraft_bot' уже существует (это хорошо).")

        await conn.close()

    except Exception as e:
        print(f"❌ Ошибка на Шаге 1: {e}")
        print("💡 СОВЕТ: Если ошибка 'role postgres does not exist', замени в коде DB_USER = 'postgres' на своё имя пользователя на маке.")
        return

    # ШАГ 2. Создаем таблицу внутри базы
    try:
        # Теперь подключаемся уже к НАШЕЙ новой базе
        conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database='stalcraft_bot')

        # Создаем таблицу
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1
            );
        ''')
        print("✅ Таблица 'users' успешно создана (или уже была).")
        await conn.close()

        print("\n🎉 ВСЁ ГОТОВО! Теперь можешь запускать своего бота (файл telebot.py)!")

    except Exception as e:
        print(f"❌ Ошибка на Шаге 2: {e}")

# Запуск скрипта
if __name__ == "__main__":
    asyncio.run(create_db_structure())
