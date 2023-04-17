import ast
import json
from tg_converter import TelegramSession
import json
import os
from pyrogram import Client, idle, enums, filters
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,
                            InlineKeyboardButton, ChatPrivileges)
import re
import random
from pyrogram.raw.functions.messages import GetAllChats
from random_username.generate import generate_username
from pyrogram.errors import FloodWait, BadRequest, PeerFlood, Unauthorized, SeeOther, Forbidden, NotAcceptable, Flood, InternalServerError, UserDeactivated, UserDeactivatedBan, ChannelsAdminPublicTooMuch, UsernameNotOccupied, UsernameInvalid, InviteRequestSent, PeerIdInvalid, ChannelInvalid, UserAlreadyParticipant
import asyncio
from russian_names import RussianNames
import pymorphy2
import phonenumbers
from phonenumbers.phonenumberutil import region_code_for_country_code
morph = pymorphy2.MorphAnalyzer()

def read_file(filename):
  with open(filename, 'r', encoding='utf-8') as f:
    data = f.read()
  f.close()
  return data

def get_base(number):
  with open(f"groups.txt", "r") as file:
    base = ast.literal_eval(file.read())
  accounts = list(set([i.split(".")[0] for i in os.listdir(f"accounts")]))
  lns = int(len(base)/len(accounts))
  data = base[number*lns:][:lns]
  return data

async def create_bot():
  with open('token.txt', 'r') as f:
    token = f.read()
  f.close()
  botapp = Client("forwarder_bot", bot_token=token)
  return botapp

class sender():
  async def app(account, proxy=True):
    with open(f'accounts/{account}.json', 'r') as f:
      data = json.load(f)
    session = TelegramSession.from_sqlite_session_file(f'accounts/{account}.session', api_id=int(data['app_id']), api_hash=data['app_hash'])
    f.close()

    pn = phonenumbers.parse(f'+{data["phone"]}')
    proxy = {
      "scheme": "socks5",
      "hostname": "geo.iproyal.com",
      "port": 42324,
      "username": "telegain",
      "password": f"TeleGain2077_country-{region_code_for_country_code(pn.country_code).lower()}"
    }

    app = await session.make_pyrogram(
      app_version=data['app_version'],
      device_model=data['device'],
      system_version=data['sdk'],
      lang_code=data['lang_pack'],
      ipv6=data['ipv6'],
      proxy=proxy
    )
    return app

  async def join_chats(app, number):
    groups = get_base(number)

    accounts = list(set([i.split(".")[0] for i in os.listdir("accounts")]))
    a = accounts.index(accounts[-1])
    if number == a:
      with open(f"groups.txt", "r") as file:
          base = ast.literal_eval(file.read())
      file.close()

      lns = len(base)-int(len(base)/len(accounts))*len(accounts)
      groups.append(base[-lns:][0])

    for group in groups:
      while True:
        try:
          if 'https://t.me/' in group:
            await app.join_chat(group)
            print (f'joined {group}')
            await asyncio.sleep(60)
            break
          else:
            chat = await app.get_chat(group)
            if chat.type == enums.ChatType.GROUP or chat.type == enums.ChatType.SUPERGROUP:
              await app.join_chat(group)
              print (f'joined {group}')
              await asyncio.sleep(60)
            break
        except UsernameNotOccupied as e:
          print (e)
          break
        except FloodWait as e:
          print (e.value)
          await asyncio.sleep(e.value)
          continue
        except InviteRequestSent as e:
          print (f'joined {group}')
          await asyncio.sleep(60)
          break
        except UsernameInvalid as e:
          print (e)
          break
        except ChannelInvalid as e:
          print (e)
          break
        except UserAlreadyParticipant as e:
          print (e)
          break

  async def interceptor(botapp, bot_username):
    with open('words.txt', 'r', encoding='utf-8') as f:
      stop_words = ast.literal_eval(f.read())
    f.close()
    # chat_id = -982679420
    # chat_id = await app.join_chat('https://t.me/+eczWSPl74YczZDcy')
    # print (chat_id.id)

    # func = GetAllChats(except_ids=[0])
    # chats = await app.invoke(func)
    # chats = chats.chats
    # for chat in chats:
    #   try:
    #     print (chat.username)
    #     await app.leave_chat(chat.username)
    #     print ('left')
    #   except:
    #     pass

    async def forwarder():
      accounts = list(set([i.split(".")[0] for i in os.listdir("accounts")]))
      async def body(account):
        app = await sender.app(account)
        await app.start()

        @app.on_message(~filters.me)
        async def reply(client, message):
          from advertools import extract_emoji
          if message.text != None and extract_emoji([message.text])['emoji_counts'][0] == 0:
            text = [morph.parse(word)[0].normal_form for word in re.findall(r'\w+', message.text.lower())]
            for word in text:
              if word in stop_words:
                admins = []
                async for member in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                  admins.append(member.user.id)
                print (admins)
                print (message.from_user.id)
                if message.from_user.id not in admins:
                  print (message.text.lower())
                  if message.from_user.username != None:
                    username = message.from_user.username
                  else:
                    username = 'None'
                  try:
                    text = f"{message.link}|divider|{message.text}|divider|{username}"
                    await app.send_message(bot_username, text)
                  except FloodWait as e:
                    print (e.value)
                    await asyncio.sleep(e.value)
                    text = f"{message.link}|divider|{message.text}"
                    await app.send_message(bot_username, text)
                break

      async def run_tasks():
          tasks = [body(i) for i in accounts]
          for task in asyncio.as_completed(tasks):
              await task
      await run_tasks()

    if not os.path.exists('chat_id.txt'):
      @botapp.on_message(filters.new_chat_members)
      async def bot(client, message):
        if not os.path.exists('chat_id.txt'):
          with open('chat_id.txt', 'w') as f:
            f.write(str(message.chat.id))
          f.close()
          await forwarder()
    else:
      await forwarder()

    @botapp.on_message(~filters.me & ~filters.new_chat_members)
    async def bot(client, message):
      with open('chat_id.txt', 'r') as f:
        chat_id = int(f.read())
      f.close()

      text = message.text
      text = text.split('|divider|')
      if text[-1] != 'None':
        buttons = [
          [  # First row
            InlineKeyboardButton(  # Opens a web URL
              "🙍‍♂️ ПОЛЬЗОВАТЕЛЬ",
              url=f'https://t.me/{text[-1]}'
            )
          ],
          [  # First row
            InlineKeyboardButton(  # Opens a web URL
              "💬 СООБЩЕНИЕ",
              url=text[0]
            )
          ]
        ]
      else:
        buttons = [
          [  # First row
            InlineKeyboardButton(  # Opens a web URL
              "💬 СООБЩЕНИЕ",
              url=text[0]
            )
          ]
        ]
      try:
        await botapp.send_message(
          chat_id,
          text[1],
          reply_markup=InlineKeyboardMarkup(buttons))
      except FloodWait as e:
        print (e.value)
        await asyncio.sleep(e.value)
        await message.forward(chat_id)