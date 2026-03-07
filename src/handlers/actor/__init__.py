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

from .register import router as register_router
from .ready import router as ready_router
from .team_arrived import router as team_arrived_router
from .stage_complete import router as stage_complete_router
from .score_entry import router as score_entry_router
from .ready_next import router as ready_next_router
from .teams_list import router as teams_list_router


router = Router()
router.include_routers(
    register_router,
    ready_router,
    team_arrived_router,
    stage_complete_router,
    score_entry_router,
    ready_next_router,
    teams_list_router
)
