from fastapi import HTTPException, status

player_not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Player not found.",
)

multiple_players_found = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Multiple players found with the same attribute.",
)

player_already_exists = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Player with this username already exists",
)
