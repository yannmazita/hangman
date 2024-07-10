from app.players.models import Player
from app.repository import DatabaseRepository


class PlayerRepository(DatabaseRepository):
    """
    Repository for performing database queries on players.
    """

    def __init__(self):
        super().__init__(Player)
