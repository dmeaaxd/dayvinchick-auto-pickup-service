import asyncio
import configparser
import os

from telethon import TelegramClient, events

from src.config import settings
from src.openai_service import OpenAIService

if not os.path.exists("photos"):
    os.makedirs("photos")

config = configparser.ConfigParser()
bot_name = 'leomatchbot'
client = TelegramClient("tg_sess", settings.TG_API_ID, settings.TG_API_HASH)

openai_service = OpenAIService()

saved_files = set()
last_buttons_message = None  # тут будем хранить последнее сообщение с кнопками


# --- TELEGRAM EVENT HANDLER ---
@client.on(events.NewMessage(from_users=bot_name))
async def handler(event):
    global last_buttons_message
    m = event.message

    # обновляем последнее сообщение с кнопками
    if m.buttons:
        last_buttons_message = m

    # сохраняем фото
    if m.media:
        file_path = await client.download_media(m, "photos/")
        if file_path and file_path not in saved_files:
            saved_files.add(file_path)
            print(f"Фото сохранено: {os.path.basename(file_path)}")

        # если есть кнопки — оцениваем фото через OpenAI
        if last_buttons_message and last_buttons_message.buttons:
            verdict = await openai_service.check_image()
            print(verdict)
            if verdict is True:
                print(f"Вердикт: 👍 Писать! (фото: {os.path.basename(file_path)})")
                button_to_click = "❤️"
            else:
                print(f"Вердикт: 👎 Не писать! (фото: {os.path.basename(file_path)})")
                button_to_click = "👎"

            # проходим по всем кнопкам и нажимаем подходящую
            for row in last_buttons_message.buttons:
                for button in row:
                    if button_to_click in button.text:
                        await last_buttons_message.click(text=button.text)
                        print(f"Кнопка '{button_to_click}' нажата!")
                        await asyncio.sleep(2)
                        return


async def main():
    await client.start()
    await client.send_message(bot_name, "/start")
    await asyncio.sleep(2)
    await client.send_message(bot_name, "1 🚀")
    print("Бот запущен, ждём анкеты...")
    await client.run_until_disconnected()


asyncio.run(main())
