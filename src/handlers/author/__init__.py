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

from aiogram import Router

from .main_menu import router as main_menu_router
from .cancel_game import router as cancel_game_router
from .create_game import router as create_game_router
from .delete_actor import router as delete_actor_router
from .delete_team import router as delete_team_router
from .participants import router as participants_router
from .registration import router as registration_router
from .start_game import router as start_game_router
from .game_status import router as game_status_router
from .finish_game import router as finish_game_router
from .edit_team import router as edit_team_router
from .edit_actor import router as edit_actor_router


router = Router()
router.include_routers(
    main_menu_router,
    cancel_game_router,
    create_game_router,
    delete_actor_router,
    delete_team_router,
    participants_router,
    registration_router,
    start_game_router,
    game_status_router,
    finish_game_router,
    edit_team_router,
    edit_actor_router,
)
