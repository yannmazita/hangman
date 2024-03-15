from uuid import UUID
from typing import Annotated

from fastapi import Depends, HTTPException, Query, Security, status
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound

from app.database import engine
from app.dependencies.users import get_own_user
from app.dependencies.tokens import validate_token
from app.models import Player, PlayerCreate, TokenData, User


async def get_own_player(
    token_data: Annotated[
        TokenData, Security(validate_token, scopes=["user:own:player"])
    ]
) -> Player:
    with Session(engine) as session:
        try:
            player = session.exec(
                select(Player).where(Player.username == token_data.username)
            ).one()
            return player
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User has no player"
            )


async def create_new_player(
    token_data: Annotated[
        TokenData, Security(validate_token, scopes=["user:own.write"])
    ],
    player: PlayerCreate,
):
    with Session(engine) as session:
        try:
            # Should not be possible, but better be bulletproof.
            session.exec(select(Player).where(Player.username == player.username)).one()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Player with this username already exists",
            )
        except NoResultFound:
            pass
    new_player = Player(playername=player.username, username=player.username)
    db_player = Player.model_validate(new_player)
    with Session(engine) as session:
        session.add(db_player)
        session.commit()
        session.refresh(db_player)
    return db_player


async def get_players(
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    with Session(engine) as session:
        players = session.exec(select(Player).offset(offset).limit(limit)).all()
        return players


async def get_player_by_id(player_id: UUID) -> Player:
    with Session(engine) as session:
        try:
            player = session.exec(select(Player).where(Player.id == player_id)).one()
            return player
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Player does not exist"
            )


async def get_player(
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    player_id: UUID,
) -> Player:
    return await get_player_by_id(player_id)


async def remove_player_by_id(player_id: UUID) -> Player:
    with Session(engine) as session:
        try:
            player = session.exec(select(Player).where(Player.id == player_id)).one()
            session.delete(player)
            session.commit()
            return player
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Player does not exist"
            )


async def remove_player(
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    player_id: UUID,
) -> Player:
    return await remove_player_by_id(player_id)


async def remove_own_player(user: Annotated[User, Depends(get_own_user)]) -> Player:
    assert user.player_id is not None
    return await remove_player_by_id(user.player_id)
