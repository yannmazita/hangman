import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.players.models import Player
from app.players.repository import PlayerRepository
from app.players.schemas import PlayerUpdate

logger = logging.getLogger(__name__)


class PlayerServiceBase:
    """
    Base class for player-related operations.

    Attributes:
        repository: The player repository to be used for operations.
    """

    def __init__(self, repository: PlayerRepository):
        self.repository = repository


class PlayerService(PlayerServiceBase):
    """
    Class for player-related operations.
    Attributes:
        repository: The player repository to be used for operations.
    """

    def __init__(self, repository: PlayerRepository):
        self.repository = repository


class PlayerAdminService(PlayerServiceBase):
    """
    Class for player-related operations.
    Attributes:
        repository: The player repository to be used for operations.
    """

    def __init__(self, repository: PlayerRepository):
        self.repository = repository

    async def update_player_playername(
        self, session: AsyncSession, id: UUID, data: PlayerUpdate
    ) -> Player:
        """
        Update a player's playername.

        Dedidacated method for player updates. If other data besides playername information is
        present, it is ignored.
        Args:
            session: The database session to be used for the operation.
            id: The ID of the player to update.
            data: The data to be used for updating the player.
        Returns:
            The updated player.
        """
        data.username = None
        data.points = None
        data.games_played = None
        data.games_won = None
        logger.debug(f"Updating playername for player with ID: {id}")
        update_player: Player = await self.repository.update_by_attribute(
            session, data, id
        )
        logger.info(f"Playername updated for player with ID: {id}")
        return update_player
