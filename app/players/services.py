import logging
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.players.exceptions import (
    multiple_players_found,
    player_already_exists,
    player_not_found,
)
from app.players.models import (
    Player,
    PlayerCreate,
    PlayerPlayernameUpdate,
)
from app.players.schemas import PlayerAttribute

logger = logging.getLogger(__name__)


class PlayerServiceBase:
    """
    Base class for player-related operations.

    Attributes:
        session: The database session to be used for operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_player(self, player: PlayerCreate) -> Player:
        """
        Create a new player.
        Args:
            player: The player data.
        Returns:
            The created player.
        """
        try:
            logger.debug(f"Attempting to create player: {player.playername}")
            query = select(Player).where(Player.playername == player.playername)
            response = await self.session.execute(query)
            existing_player: Player | None = response.scalar_one_or_none()

            if existing_player:
                logger.warning(f"Player already exists: {player.playername}")
                raise player_already_exists

            new_player = Player(
                id=uuid4(),
                playername=player.playername,
                username=player.username,
            )
            db_player = Player.model_validate(new_player)

            logger.debug(f"Adding new player to session: {db_player}")
            self.session.add(db_player)

            logger.debug("Committing session")
            await self.session.commit()

            logger.debug("Refreshing session")
            await self.session.refresh(db_player)

            logger.info(f"Player created successfully: {db_player.playername}")
            return db_player
        except IntegrityError as e:
            logger.error(f"IntegrityError occurred: {e}", exc_info=False)
            raise e
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except HTTPException as e:
            logger.error(f"HTTPException occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e

    async def get_player_by_attribute(
        self, attribute: PlayerAttribute, value: str
    ) -> Player:
        """
        Get a player by a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
        Returns:
            The player with the specified attribute and value.
        """
        try:
            logger.debug(f"Attempting to get player by {attribute.value}: {value}")
            query = select(Player).where(getattr(Player, attribute.value) == value)
            response = await self.session.execute(query)
            player = response.scalar_one()
            logger.info(f"Player found: {player.playername}")
            return player
        except MultipleResultsFound:
            logger.error(
                f"Multiple players found for {attribute.value} = {value}",
                exc_info=False,
            )
            raise multiple_players_found
        except NoResultFound:
            logger.warning(
                f"No player found for {attribute.value} = {value}", exc_info=False
            )
            raise player_not_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e

    async def update_player_by_attribute(
        self, attribute: PlayerAttribute, value: str, player: PlayerCreate
    ) -> Player:
        """
        Update a player using a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
            player: The new player data.
        Returns:
            The updated player.
        """
        try:
            logger.debug(f"Attempting to update player by {attribute.value}: {value}")
            player_db = await self.get_player_by_attribute(attribute, value)
            player_data = player.model_dump()
            for key, value in player_data.items():
                if key != "id":
                    setattr(player_db, key, value)
            self.session.add(player_db)
            await self.session.commit()
            await self.session.refresh(player_db)
            logger.info(f"Player updated successfully: {player_db.playername}")
            return player_db
        except NoResultFound:
            logger.warning(
                f"No player found for {attribute.value} = {value}", exc_info=False
            )
            raise player_not_found
        except MultipleResultsFound:
            logger.error(
                f"Multiple players found for {attribute.value} = {value}",
                exc_info=False,
            )
            raise multiple_players_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e

    async def delete_player(self, player: Player) -> Player:
        """
        Delete a player.
        Args:
            player: The player to delete.
        Returns:
            The deleted player.
        """
        try:
            logger.debug(f"Attempting to delete player: {player.playername}")
            await self.session.delete(player)
            await self.session.commit()
            logger.info(f"Player deleted successfully: {player.playername}")
            return player
        except NoResultFound:
            logger.warning(
                f"No player found to delete: {player.playername}", exc_info=False
            )
            raise player_not_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e

    async def delete_player_by_attribute(
        self, attribute: PlayerAttribute, value: str
    ) -> Player:
        """
        Delete a player using a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
        Returns:
            The deleted player.
        """
        try:
            logger.debug(f"Attempting to delete player by {attribute.value}: {value}")
            player = await self.get_player_by_attribute(attribute, value)
            await self.session.delete(player)
            await self.session.commit()
            logger.info(f"Player deleted successfully: {player.playername}")
            return player
        except NoResultFound:
            logger.warning(
                f"No player found for {attribute.value} = {value}", exc_info=False
            )
            raise player_not_found
        except MultipleResultsFound:
            logger.error(
                f"Multiple players found for {attribute.value} = {value}",
                exc_info=False,
            )
            raise multiple_players_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e

    async def get_players(self, offset: int = 0, limit: int = 100):
        """
        Get all players.
        Args:
            offset: The number of players to skip.
            limit: The maximum number of players to return.
        Returns:
            The list of players.
        """
        try:
            logger.debug(f"Fetching players with offset: {offset}, limit: {limit}")
            total_count_query = select(func.count()).select_from(Player)
            total_count_response = await self.session.execute(total_count_query)
            total_count: int = total_count_response.scalar_one()

            players_query = select(Player).offset(offset).limit(limit)
            players_response = await self.session.execute(players_query)
            players = players_response.scalars().all()
            logger.info(f"Fetched {len(players)} players")
            return players, total_count
        except NoResultFound:
            logger.warning("No players found", exc_info=False)
            raise player_not_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e


class PlayerService(PlayerServiceBase):
    """
    Class for player-related operations.
    Attributes:
        session: The database session to be used for operations.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)


class PlayerAdminService(PlayerServiceBase):
    """
    Class for player-related operations.
    Attributes:
        session: The database session to be used for operations.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def update_player_playername_by_attribute(
        self,
        attribute: PlayerAttribute,
        value: str,
        new_playername: PlayerPlayernameUpdate,
    ) -> Player:
        """
        Update a player's playername using a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
            new_playername: The new playername.
        Returns:
            The updated player.
        """
        try:
            logger.debug(
                f"Updating playername for player with {attribute.value}: {value}"
            )
            player = await self.get_player_by_attribute(attribute, value)
            player.playername = new_playername.playername
            self.session.add(player)
            await self.session.commit()
            await self.session.refresh(player)
            logger.info(
                f"Playername updated to {new_playername.playername} for player: {player.playername}"
            )
            return player
        except NoResultFound:
            logger.warning(
                f"No player found for {attribute.value} = {value}", exc_info=False
            )
            raise player_not_found
        except MultipleResultsFound:
            logger.error(
                f"Multiple players found for {attribute.value} = {value}",
                exc_info=False,
            )
            raise multiple_players_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e
