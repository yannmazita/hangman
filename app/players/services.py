from uuid import uuid4
from sqlmodel import Session, func, select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from app.players.exceptions import (
    player_not_found,
    multiple_players_found,
    player_already_exists,
)
from app.players.models import Player, PlayerCreate
from app.players.schemas import PlayerAttribute


class PlayerServiceBase:
    """
    Base class for player-related operations.

    Attributes:
        session: The database session to be used for operations.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_player(self, player: PlayerCreate) -> Player:
        """
        Create a new player.
        Args:
            player: The player data.
        Returns:
            The created player.
        """
        try:
            self.session.exec(
                select(Player).where(Player.playername == player.playername)
            ).one()
            raise player_already_exists
        except NoResultFound:
            pass
        new_player = Player(
            id=uuid4(), playername=player.playername, username=player.username
        )
        db_player = Player.model_validate(new_player)
        self.session.add(db_player)
        self.session.commit()
        self.session.refresh(db_player)
        return db_player

    def get_player_by_attribute(self, attribute: PlayerAttribute, value: str) -> Player:
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
            return self.session.exec(query).one()
        except NoResultFound:
            raise player_not_found
        except MultipleResultsFound:
            raise multiple_players_found

    def update_player_by_attribute(
        self, attribute: PlayerAttribute, value: str, player: PlayerCreate
    ) -> Player:
        """
        Update a player by a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
            player: The new player data.
        Returns:
            The updated player.
        """
        try:
            player_db = self.get_player_by_attribute(attribute, value)
        except NoResultFound:
            raise player_not_found
        except MultipleResultsFound:
            raise multiple_players_found
        player_data = player.model_dump()
        for field, value in player_data.items():
            setattr(player_db, field, value)
        self.session.add(player_db)
        self.session.commit()
        self.session.refresh(player_db)

        return player_db

    def delete_player(self, player: Player) -> Player:
        """
        Delete a player.
        Args:
            player: The player to delete.
        Returns:
            The deleted player.
        """
        try:
            self.session.delete(player)
            self.session.commit()
        except NoResultFound:
            raise player_not_found

        return player

    def delete_player_by_attribute(
        self, attribute: PlayerAttribute, value: str
    ) -> Player:
        """
        Delete a player by a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
        Returns:
            The deleted player.
        """
        try:
            player = self.get_player_by_attribute(attribute, value)
            self.session.delete(player)
            self.session.commit()
        except NoResultFound:
            raise player_not_found
        except MultipleResultsFound:
            raise multiple_players_found
        return player

    def get_players(self, offset: int = 0, limit: int = 100):
        """
        Get all players.
        Args:
            offset: The number of records to skip.
            limit: The maximum number of records to return.
        Returns:
            A tuple containing the list of players and the total number of players.
        """
        total_count_statement = select(func.count()).select_from(Player)
        total_count: int = self.session.exec(total_count_statement).one()
        players = self.session.exec(select(Player).offset(offset).limit(limit)).all()
        return players, total_count


class PlayerService(PlayerServiceBase):
    """
    Class for player-related operations.

    Attributes:
        session: The database session to be used for operations.
    """

    def __init__(self, session: Session):
        super().__init__(session)


class PlayerAdminService(PlayerServiceBase):
    """
    Class for player-related operations.
    Attributes:
        session: The database session to be used for operations.
    """

    def __init__(self, session: Session):
        super().__init__(session)
