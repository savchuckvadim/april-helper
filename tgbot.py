import os

from aiogram import Bot
from aiogram.types import FSInputFile

from dotenv import load_dotenv
import logging


load_dotenv()

# Настройка логирования
logging.basicConfig(
    filename="info.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class TelegramBot:
    bot = ""  # экземпляр этого же класа

    def __init__(self) -> None:
        # Настройка логирования

        self.bot = Bot(token=os.getenv("BOT_TOKEN"))
        self.GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
        self.set_bot(bot=self)  # Создается класс один раз

    @classmethod
    def set_bot(cls, bot):
        cls.bot = bot  # переопределение string в TelegramBot
        return

    @classmethod
    def get_bot(cls):
        print(f"ЗАПРОСИЛИ БОТА: {cls.bot}")
        return cls.bot
        # Закрываем соединение с ботом

    async def send_message(self, message):
        logger.info(f"bot send_message: {message}")

        if len(message) > 4096:
            for x in range(0, len(message), 4096):

                await self.bot.send_message(
                    chat_id=self.GROUP_CHAT_ID,
                    text=message[x : x + 4096],
                    parse_mode="Markdown",
                )
            return
        await self.bot.send_message(
            chat_id=self.GROUP_CHAT_ID, text=message, parse_mode="Markdown"
        )


    async def send_message_admin_error(self, message, domain):
        logger.info(f"bot send_message_admin_error: {message} | auth_data: {domain}")

        if len(message) > 4096:
            for x in range(0, len(message), 4096):
                await self.bot.send_message(
                    chat_id=os.getenv("ERROR_ID_CHAT"),
                    text=message[x : x + 4096],
                    parse_mode="MarkdownV2",
                )
            await self.bot.send_message(
                chat_id=os.getenv("ERROR_ID_CHAT"),
                text=f"domain: ```json\n{domain}",
                parse_mode="MarkdownV2",
            )
            return
        await self.bot.send_message(
            chat_id=os.getenv("ERROR_ID_CHAT"),
            text=message,
        )
        await self.bot.send_message(
            chat_id=os.getenv("ERROR_ID_CHAT"),
            text=f"domain: ```json\n{domain}```",
            parse_mode="MarkdownV2",
        )

    async def send_message_admin(self, message):
        logger.info(f"bot send_message_admin: {message}")

        if len(message) > 4096:
            for x in range(0, len(message), 4096):
                await self.bot.send_message(
                    chat_id=os.getenv("ADMIN_ID"),
                    text=message[x : x + 4096],
                    parse_mode="MarkdownV2",
                )
            return
        await self.bot.send_message(
            chat_id=os.getenv("ADMIN_ID"),
            text=message,
            parse_mode="MarkdownV2",
        )

    async def send_message_portal(self, chat_id, message):
        logger.info(f"bot send_message_portal: {message}")

        if chat_id is None or chat_id == "":
            chat_id = os.getenv("ADMIN_ID")
        if len(message) > 4096:
            for x in range(0, len(message), 4096):
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message[x : x + 4096],
                    parse_mode="MarkdownV2",
                )
                return
        await self.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="MarkdownV2",
        )

    async def send_message_json(self, message):
        logger.info(f"bot send_message_json: {message}")

        if len(message) > 4096:

            for x in range(0, len(message), 4096):
                await self.bot.send_message(
                    chat_id=self.GROUP_CHAT_ID,
                    text=message[x : x + 4096],
                    parse_mode="MarkdownV2",
                )
            return
        await self.bot.send_message(chat_id=self.GROUP_CHAT_ID, text=message)

    async def send_file_json(self, file, message=None):
        logger.info(f"bot send_file_json: {message}")

        # Проверка существования файла
        if not os.path.isfile(file):
            logger.warning(f"Ошибка: Файл не найден по пути {file}")
            return
        input_file = FSInputFile("./" + file, filename="data.json")
        try:
            await self.bot.send_document(
                chat_id=self.GROUP_CHAT_ID, document=input_file, caption=message
            )
        except Exception as e:
            logger.error(f"bot send_message_json: {str(e)}")

    async def close(self):
        await self.bot.session.close()
