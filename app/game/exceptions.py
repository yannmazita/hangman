from fastapi import HTTPException, status
from uuid import UUID


class GameException(Exception):
    """Base class for game exceptions"""

    pass


class GameOver(GameException):
    """Raised when a game is over."""

    def __init__(self, user_id: UUID):
        self.message = f"Game over for user {user_id}."
        super().__init__(self.message)


game_not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Game not found.",
)

multiple_games_found = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Multiple games found with the same attribute.",
)

game_already_exists = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Game already exists for this player.",
)
