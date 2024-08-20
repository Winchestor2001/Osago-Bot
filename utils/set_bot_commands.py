from aiogram import types


async def set_default_commands(bot):
    await bot.set_my_commands(
        [
            types.BotCommand(command="start", description="Запустить бота"),
            types.BotCommand(command="menu", description="Главный меню"),
            types.BotCommand(command="cancel", description="Отменить/Назад"),
        ]
    )
