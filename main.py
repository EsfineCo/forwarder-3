from runner import sender, create_bot
import asyncio
import os
from pyrogram import idle
import random
from russian_names import RussianNames
from pyrogram.errors import PeerFlood, UserDeactivated, UserDeactivatedBan, MessageEmpty
from Accounts import Main

async def join_chats():
    async def body(account):
        number = accounts.index(account)
        app = await sender.app(account)
        await app.start()
        await asyncio.sleep(number*5)
        await sender.join_chats(app, number)
        await app.stop()

    accounts = list(set([i.split(".")[0] for i in os.listdir("accounts")]))
    async def run_tasks():
        tasks = [body(i) for i in accounts]
        for task in asyncio.as_completed(tasks):
            await task
    await run_tasks()

async def main():
    #Main.download(1)
    await join_chats()
    
    # botapp = await create_bot()

    # await botapp.start()
    # me = await botapp.get_me()
    # print (me.username)
    # await sender.interceptor(botapp, me.username)
    # await idle()

if __name__ == "__main__":
    asyncio.run(main())