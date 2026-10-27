
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message
from dotenv import load_dotenv
from service import *
import asyncio
import os
from keyboard import *
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class TaskStates(StatesGroup):
    waiting_create = State()
    waiting_update = State()
    waiting_update_id = State()

load_dotenv()
token = os.getenv("BOT_TOKEN")

bot = Bot(token=token)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_bot(message: Message):
    user = message.from_user
    user_data = await get_user(user.id)
    if user_data:
        await message.answer(
            f"Здарова, {user.full_name}! 😎\n\n"
            "Добро пожаловать в Task Manager!\n\n"
            "Команды:\n"
            "/create Название — создать задачу\n"
            "/tasks — посмотреть задачи\n"
            "/update ID Новое название — изменить задачу\n"
            "/delete ID — удалить задачу\n"
            "/status ID — изменить статус\n"
            "/help — помощь",
            reply_markup=main_menu
        )
    else:
        status = await created_user(user.username, user.full_name, user.id)
        if status:
            await message.answer(
                f"Добро пожаловать, {user.full_name}! 🔥\n\n"
                "Используй /help для просмотра команд."
            )
        else:
            await message.answer("Не получилось создать профиль Попробуй позже.")


@dp.message(Command("help"))
@dp.message(F.text == "🆘 Помощь")
async def help_command(message: Message):
    await message.answer(
        "📋 TASK MANAGER\n\n"
        "➕ /create Название задачи\n"
        "Создать задачу.\n\n"
        "📋 /tasks\n"
        "Посмотреть все свои задачи.\n\n"
        "✏️ /update ID Новое название\n"
        "Изменить название задачи.\n"
        "Пример: /update 1 Учить Python\n\n"
        "🗑 /delete ID\n"
        "Удалить задачу.\n"
        "Пример: /delete 1\n\n"
        "🔄 /status ID\n"
        "Изменить статус задачи.\n"
        "Пример: /status 1\n\n"
        "Статус: False — не выполнена, True — выполнена."
    )


@dp.message(Command("create"))
@dp.message(F.text == "➕ Новая задача")
async def create_task_handler(message: Message, state: FSMContext):
    await state.set_state(TaskStates.waiting_create)
    await message.answer("Напиши название задачи:")

@dp.message(TaskStates.waiting_create)
async def create_task_finish(message: Message, state: FSMContext):
    title = (message.text or "").strip()
    if not title:
        await message.answer("Название не должно быть пустым 😅")
        return
    if len(title) > 200:
        await message.answer("Максимум 200 символов.")
        return
    status = await create_task(message.from_user.id, title)
    await state.clear()
    if status:
        await message.answer("✅ Задача создана!")
    else:
        await message.answer("Не получилось создать задачу 😭")



@dp.message(Command("tasks"))
@dp.message(F.text == "🎫 Мои задачи")
async def my_tasks(message: Message):
    tasks = await get_user_tasks(message.from_user.id)
    if not tasks:
        await message.answer("У тебя пока нет задач")
        return
    text = "📋 ТВОИ ЗАДАЧИ\n\n"
    for task in tasks:
        text += (
            f"🆔 ID: {task['task_id']}\n"
            f"📝 Название: {task['title']}\n"
            f"📌 Статус: {'True ✅' if task['status'] else 'False ❌'}\n\n")
    await message.answer(text)



@dp.message(Command("update"))
@dp.message(F.text == "Обновить задачу")
async def update_task_start(message: Message, state: FSMContext):
    await state.set_state(TaskStates.waiting_update_id)
    await message.answer("Напиши ID задачи:")

@dp.message(TaskStates.waiting_update_id)
async def update_task_id(message: Message, state: FSMContext):
    try:
        task_id = int((message.text or "").strip())
        if task_id <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введи правильный ID задачи.")
        return
    task = await get_task(task_id, message.from_user.id)
    if not task:
        await message.answer("Задача не найдена 😭")
        return
    await state.update_data(task_id=task_id)
    await state.set_state(TaskStates.waiting_update)
    await message.answer("Напиши новое название задачи:")


@dp.message(TaskStates.waiting_update)
async def update_task_finish(message: Message, state: FSMContext):
    title = (message.text or "").strip()
    if not title:
        await message.answer("Название не должно быть пустым 😅")
        return
    if len(title) > 200:
        await message.answer("Максимум 200 символов.")
        return
    data = await state.get_data()
    status = await update_task(data["task_id"], message.from_user.id, title)
    await state.clear()
    if status:
        await message.answer("✅ Задача обновлена!")
    else:
        await message.answer("Не получилось изменить задачу 😭")




@dp.message(Command("delete"))
async def delete_task_handler(message: Message, command: CommandObject):
    try:
        task_id = int((command.args or "").strip())
        if task_id <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Укажи ID задачи\nПример: /delete 1")
        return
    status = await delete_task(task_id, message.from_user.id)
    if status:
        await message.answer("🗑 Задача удалена!")
    else:
        await message.answer("Задача не найдена")



@dp.message(Command("status"))
async def change_task_status(message: Message, command: CommandObject):
    try:
        task_id = int((command.args or "").strip())
        if task_id <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пример: /status 1")
        return
    status = await change_status(task_id, message.from_user.id)
    if status is None:
        await message.answer("Задача не найдена или произошла ошибка")
    elif status:
        await message.answer("✅ Задача выполнена: True")
    else:
        await message.answer("❌ Задача не выполнена: False")



async def main():
    await create_table()
    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())