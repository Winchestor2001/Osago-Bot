import asyncio
from pyrogram import Client, types

# api_id = 11487512
# api_hash = "236779b4ecf3f49dabe5d358db2a01ed"


async def main():
    users = [1635543672]
    message = "Новая телега @osagomaksc и новый бот @Osagoa_bot"
    # with open('../users_data.txt', 'r', encoding='utf-8') as file:
    #     for user in file.read().split("\n"):
    #         users.append(user.split(":")[0])
    # print(users)
    async with Client("tg_session/osago") as app:
        for user in users:
            u = await app.get_users([user])
            print(u)
            # await app.send_message(chat_id=user, text=message)
            await asyncio.sleep(.5)


asyncio.run(main())
