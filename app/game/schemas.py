from enum import Enum


class GameAttribute(Enum):
    ID = "id"
    PLAYER_ID = "player_id"


class GameStatsAttribute(Enum):
    GUESSED_POSITIONS = "guessed_positions"
    GUESSED_LETTERS = "guessed_letters"
    TRIES_LEFT = "tries_left"
    SUCCESSFUL_GUESSES = "successful_guesses"
    GAME_STATUS = "game_status"
