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
            query = select(Player).where(Player.playername == player.playername)
            response = await self.session.execute(query)
            existing_player: Player | None = response.scalar_one_or_none()

            if existing_player:
                raise player_already_exists

            new_player = Player(
                id=uuid4(),
                playername=player.playername,
                username=player.username,
            )
            db_player = Player.model_validate(new_player)

            self.session.add(db_player)

            await self.session.commit()

            await self.session.refresh(db_player)

            return db_player
        except IntegrityError as e:
            raise e
        except SQLAlchemyError as e:
            raise e
        except HTTPException as e:
            raise e
        except Exception as e:
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
            query = select(Player).where(getattr(Player, attribute.value) == value)
            response = await self.session.execute(query)
            player = response.scalar_one()

            return player
        except MultipleResultsFound:
            raise multiple_players_found
        except NoResultFound:
            raise player_not_found
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
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
            player_db = await self.get_player_by_attribute(attribute, value)
            player_data = player.model_dump()
            for key, value in player_data.items():
                if key != "id":
                    setattr(player_db, key, value)
            self.session.add(player_db)
            await self.session.commit()
            await self.session.refresh(player_db)

            return player_db
        except NoResultFound:
            raise player_not_found
        except MultipleResultsFound:
            raise multiple_players_found
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
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
            await self.session.delete(player)
            await self.session.commit()

            return player
        except NoResultFound:
            raise player_not_found
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
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
            player = await self.get_player_by_attribute(attribute, value)
            await self.session.delete(player)
            await self.session.commit()

            return player
        except NoResultFound:
            raise player_not_found
        except MultipleResultsFound:
            raise multiple_players_found
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
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
            total_count_query = select(func.count()).select_from(Player)
            total_count_response = await self.session.execute(total_count_query)
            total_count: int = total_count_response.scalar_one()

            players_query = select(Player).offset(offset).limit(limit)
            players_response = await self.session.execute(players_query)
            players = players_response.scalars().all()

            return players, total_count
        except NoResultFound:
            raise player_not_found
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
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
            player = await self.get_player_by_attribute(attribute, value)
            player.playername = new_playername.playername
            self.session.add(player)
            await self.session.commit()
            await self.session.refresh(player)

            return player
        except NoResultFound:
            raise player_not_found
        except MultipleResultsFound:
            raise multiple_players_found
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
            raise e
