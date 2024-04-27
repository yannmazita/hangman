from typing import Annotated

from fastapi import Depends, APIRouter

router = APIRouter(
    prefix="/game",
    tags=["game"],
)
