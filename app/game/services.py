import logging
from uuid import UUID

import aiohttp
import requests
from sqlalchemy.ext.asyncio import AsyncSession

from app.game.config import MAX_TRIES, MAX_WORD_LENGTH
from app.game.exceptions import GameOver
from app.game.models import Game
from app.game.repository import GameRepository
from app.players.models import Player
from app.players.repository import PlayerRepository

logger = logging.getLogger(__name__)


class GameServiceBase:
    """
    Base class for game-related operations.

    Attributes:
        game_repository: The game repository to be used for operations.
        player_repository: The player repository to be used for operations.
    """

    def __init__(
        self, game_repository: GameRepository, player_repository: PlayerRepository
    ) -> None:
        self.game_repository = game_repository
        self.player_repository = player_repository


class GameService(GameServiceBase):
    """
    Class for game-related operations.

    Attributes:
        repository: The game repository to be used for operations.
    """

    def __init__(
        self, game_repository: GameRepository, player_repository: PlayerRepository
    ) -> None:
        super().__init__(game_repository, player_repository)

    async def _get_random_word(self, game: Game) -> Game:
        """
        Gets a random word from the Internet.

        This method queries random-word-api to get random words from.

        Args:
            game: The game to get the random word for.
        Returns:
            The game with the random word.
        """
        word_to_guess: str = ""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://random-word-api.herokuapp.com/word?number=1"
                ) as response:
                    response = await response.json()
            while len(response[0]) > MAX_WORD_LENGTH:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://random-word-api.herokuapp.com/word?number=1"
                    ) as response:
                        response = await response.json()
            word_to_guess = response[0]

        except requests.exceptions.ConnectionError as e:
            word_to_guess = (
                "computer"  # very quick fix, need to integrate local word source
            )

        except Exception as e:
            word_to_guess = "computer"

        game.word_to_guess = word_to_guess
        logger.debug(f"Got random word for game {game.id}")
        logger.debug(f"Word to guess: {word_to_guess}")
        return game

    async def _construct_word_progress(self, game: Game) -> Game:
        """
        Contructs the word in its current state of discovery.

        Only the correctly guessed letters are present. Other letters are replaced with '*'.

        Args:
            game: The game to construct the word progress for.
        Returns:
            The game with the constructed word progress.
        """

        if not game.word_progress:
            word_progress = "*" * len(game.word_to_guess)
        else:
            word_progress_split: list[str] = list(game.word_progress)
            for pos in game.guessed_positions:
                word_progress_split[pos] = game.word_to_guess[pos]
            word_progress = "".join(word_progress_split)
        game.word_progress = word_progress
        logger.debug(f"Constructed word progress for game {game.id}")
        logger.debug(f"Word progress: {word_progress}")
        return game

    async def _update_guessed_positions(self, game: Game, character: str) -> Game:
        """
        Updates the positions of guessed characters.

        After updating the guessed_positions list this method calls construct_word_progress() and
        updates tries_left.

        Args:
            game: The game to update the guessed positions for.
            character: The guessed character.
        Returns:
            The game with the updated guessed positions.
        """

        guessed_positions = game.guessed_positions
        guessed_corretly: bool = False

        for pos, car in enumerate(game.word_to_guess):
            if character == car:
                guessed_positions.append(pos)
                guessed_corretly = True
                game.guessed_positions = guessed_positions

        updated_game = await self._construct_word_progress(game)

        if not guessed_corretly:
            tries_left = game.tries_left
            updated_game.tries_left = tries_left - 1
        logger.debug(f"Updated guessed positions for game {updated_game.id}")
        return updated_game

    async def _update_guessed_letters(self, game: Game, character: str) -> Game:
        """
        Updates the guessed letters list.

        This method appends the guessed character to the guessed_letters list.
        Whether the character is correct or not.

        Args:
            game: The game to update the guessed letters for.
            character: The guessed character.
        Returns:
            The game with the updated guessed letters.
        """
        if character not in game.guessed_letters:
            guessed_letters = game.guessed_letters
            guessed_letters.append(character)
            game.guessed_letters = guessed_letters
        logger.debug(f"Updated guessed letters for game {game.id}")
        return game

    async def _update_game_status(self, game: Game) -> Game:
        """
        Updates the game status.

        Args:
            game: The game to update the status for.
        Returns:
            The game with the updated status.
        """

        if game.game_status == 0:
            if game.tries_left == 0:
                game.game_status = -1
            elif game.word_to_guess == game.word_progress:
                game.game_status = 1
                game.successful_guesses += +1
            else:
                game.game_status = 0
        logger.debug(f"Updated game status for game {game.id}")
        return game

    async def _clear_game(self, game: Game) -> Game:
        """
        Clears the game.
        Args:
            game: The game to clear.
        Returns:
            The cleared game.
        """
        clean_game = Game(
            word_to_guess="",
            word_progress="",
            guessed_positions=[],
            guessed_letters=[],
            tries_left=MAX_TRIES,
            game_status=0,
        )
        clean_game.id = game.id
        clean_game.player_id = game.player_id
        clean_game.successful_guesses = game.successful_guesses
        logger.debug(f"Cleared game for game {game.id}")
        return clean_game

    async def start_game(self, session: AsyncSession, player_id: UUID) -> Game:
        """
        Starts a new game.
        Args:
            session: The database session to be used for the operation.
            player_id: The id of the player to start the game for.
        Returns:
            The game.
        """

        player: Player = await self.player_repository.get_by_attribute(
            session, player_id
        )
        game: Game = await self.game_repository.get_by_attribute(
            session, player_id, "player_id"
        )
        started_game = await self._construct_word_progress(
            await self._get_random_word(await self._clear_game(game))
        )
        logger.info(f"Started game for player {player.id}")
        updated_game: Game = await self.game_repository.update_by_attribute(
            session, started_game, game.id
        )
        logger.debug(f"Updated game for player {player.id}")
        return updated_game

    async def end_game(self, session: AsyncSession, player_id: UUID) -> Game:
        """
        Ends the game.
        Args:
            session: The database session to be used for the operation.
            player_id: The id of the player to end the game for.
        Returns:
            The game.
        """
        game: Game = await self.game_repository.get_by_attribute(
            session, player_id, "player_id"
        )
        ended_game = await self._clear_game(game)
        logger.info(f"Ended game for player {player_id}")
        return ended_game

    async def continue_game(self, session: AsyncSession, player_id: UUID) -> Game:
        """
        Continues the game.
        Args:
            session: The database session to be used for the operation.
            player_id: The id of the player to continue the game for.
        Returns:
            The game.
        """
        started_game: Game = await self.start_game(session, player_id)
        logger.info(f"Continued game for player {player_id}")
        updated_game: Game = await self.game_repository.update_by_attribute(
            session, started_game, started_game.id
        )
        logger.debug(f"Updated game for player {player_id}")
        return updated_game

    async def update_game_state(
        self, session: AsyncSession, game_id: UUID, character: str
    ) -> Game:
        """
        Updates the game state.
        Args:
            session: The database session to be used for the operation.
            game_id: The id of the game to update the state for.
            character: The guessed character.
        Returns:
            The game.
        """
        game: Game = await self.game_repository.get_by_attribute(session, game_id)
        if game.tries_left == 0:
            raise GameOver(game.player_id)
        game_updated_guessed_postions: Game = await self._update_guessed_positions(
            game, character
        )
        logger.debug(f"Game : {game_updated_guessed_postions}")
        game_updated_guessed_letters: Game = await self._update_guessed_letters(
            game_updated_guessed_postions, character
        )
        logger.debug(f"Game : {game_updated_guessed_letters}")
        game_updated_game_status: Game = await self._update_game_status(
            game_updated_guessed_letters
        )
        logger.debug(f"Game : {game_updated_game_status}")
        logger.info(f"Updated game state for game {game.id}")
        updated_game: Game = await self.game_repository.update_by_attribute(
            session, game, game_id
        )
        logger.debug(f"Updated game for game {game.id}")
        return updated_game
