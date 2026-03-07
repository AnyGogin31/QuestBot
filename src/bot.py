#  QuestBot
#  Copyright (C) 2026 AnyGogin31
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from redis.asyncio import Redis

from .configs import bot_config, redis_config
from .database import engine
from .handlers import all_handlers
from .utils.dispatcher import include_handlers
from .utils.logging import get_logger


_logger = get_logger(__name__)


async def create_bot():
    token = bot_config.token.get_secret_value()
    default = DefaultBotProperties(
        parse_mode=ParseMode.HTML, link_preview_is_disabled=True
    )

    return Bot(token=token, default=default)


async def create_dispatcher():
    redis = Redis.from_url(redis_config.url)
    storage = RedisStorage(redis)

    return Dispatcher(storage=storage)


async def start_bot():
    bot = await create_bot()
    dispatcher = await create_dispatcher()

    include_handlers(dispatcher, all_handlers)

    _logger.info("Запуск бота в режиме polling...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot)
    except Exception as e:
        _logger.exception("Ошибка во время работы polling: %s", e)
    finally:
        _logger.info("Остановка бота...")
        await bot.session.close()
        await engine.dispose()
        _logger.info("Бот остановлен")
