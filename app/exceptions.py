from uuid import UUID


class GameException(Exception):
    """Base class for game exceptions"""

    pass


class NoGameInstance(GameException):
    """Raised when a user has no game instance."""

    def __init__(self, user_id: UUID):
        self.message = f"User {user_id} has no game instance."
        super().__init__(self.message)


class GameOver(GameException):
    """Raised when a game is over."""

    def __init__(self, user_id: UUID):
        self.message = f"Game over for user {user_id}."
        super().__init__(self.message)
