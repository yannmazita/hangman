from typing import Annotated

from fastapi import Depends, APIRouter

from app.dependencies.players import (
    get_own_player,
    create_new_player,
    get_players,
    get_player,
    remove_player,
    remove_own_player,
)
from app.models import Player, PlayerRead

router = APIRouter(
    prefix="/players",
    tags=["players"],
)


@router.post("/", response_model=PlayerRead)
async def create_player(player: Annotated[Player, Depends(create_new_player)]):
    return player


@router.get("/id={player_id}", response_model=PlayerRead)
async def read_player(player: Annotated[Player, Depends(get_player)]):
    return player


@router.get("/", response_model=list[PlayerRead])
async def read_players(
    players: Annotated[list[Player], Depends(get_players)],
):
    return players


@router.get("/me", response_model=PlayerRead)
async def read_own_player(current_player: Annotated[Player, Depends(get_own_player)]):
    return current_player


@router.delete("/id={player_id}", response_model=PlayerRead)
async def delete_player(player: Annotated[Player, Depends(remove_player)]):
    return player


@router.delete("/me", response_model=PlayerRead)
async def delete_own_player(player: Annotated[Player, Depends(remove_own_player)]):
    return player
