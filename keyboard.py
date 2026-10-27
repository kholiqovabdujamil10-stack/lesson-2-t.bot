from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎫 Мои задачи"),KeyboardButton(text="➕ Новая задача")],
        [KeyboardButton(text="🆘 Помощь"), KeyboardButton(text="Обновить задачу")],
    ],
    resize_keyboard=True
)