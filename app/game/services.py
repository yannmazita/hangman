import logging
from uuid import UUID, uuid4

import aiohttp
import requests
from fastapi import HTTPException, status
from sqlalchemy.exc import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.game.config import MAX_TRIES, MAX_WORD_LENGTH
from app.game.exceptions import (
    GameOver,
    game_already_exists,
    game_not_found,
    multiple_games_found,
)
from app.game.models import Game
from app.game.schemas import GameAttribute
from app.players.models import Player
from app.players.schemas import PlayerAttribute
from app.players.services import PlayerService

logger = logging.getLogger(__name__)


class GameServiceBase:
    """
    Base class for game-related services.

    Attributes:
        session: The database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_new_game(self, player: Player) -> Game:
        """
        Creates a new game.
        Args:
            player: The player to create the game for.
        Returns:
            The created game.
        """
        try:
            query = select(Game).where(Game.player_id == player.id)
            response = await self.session.execute(query)
            existing_game: Game | None = response.scalar_one_or_none()

            if existing_game:
                raise game_already_exists

            new_game = Game(
                id=uuid4(),
                player_id=player.id,
            )
            db_game = Game.model_validate(new_game)

            self.session.add(db_game)

            await self.session.commit()

            await self.session.refresh(db_game)
            return db_game

        except IntegrityError as e:
            raise e
        except SQLAlchemyError as e:
            raise e
        except HTTPException as e:
            raise e
        except Exception as e:
            raise e

    async def get_game_by_attribute(self, attribute: GameAttribute, value: str) -> Game:
        """
        Get a game by a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
        Returns:
            The game with the specified attribute and value.
        """
        try:
            query = select(Game).where(getattr(Game, attribute.value) == value)
            response = await self.session.execute(query)
            game = response.scalar_one()

            return game
        except MultipleResultsFound:
            raise multiple_games_found
        except NoResultFound:
            raise game_not_found
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
            raise e

    async def update_game_by_attribute(
        self, attribute: GameAttribute, value: str, game: Game
    ) -> Game:
        """
        Update a user using a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
            game: The new game data.
        Returns:
            The updated game.
        """
        try:
            game_db: Game = await self.get_game_by_attribute(attribute, value)
            logger.debug(f"Found game: {game_db})")

            game_data = game.model_dump()
            for key, val in game_data.items():
                if key != "id":
                    setattr(game_db, key, val)
                    logger.debug(f"Setting {key} to {val}")

            self.session.add(game_db)
            logger.debug(f"Added game to session: {game_db})")
            await self.session.commit()
            logger.debug(f"Committed session for game: {game_db}")
            await self.session.refresh(game_db)
            logger.debug(f"Refreshed game: {game_db}")

            return game_db
        except NoResultFound:
            raise game_not_found
        except MultipleResultsFound:
            raise multiple_games_found
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
            raise e

    async def delete_game(self, game: Game) -> Game:
        """
        Delete a game.
        Args:
            game: The game to delete.
        Returns:
            The deleted game.
        """
        try:
            await self.session.delete(game)
            await self.session.commit()

            return game
        except NoResultFound:
            raise game_not_found
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
            raise e

    async def delete_game_by_attribute(
        self, attribute: GameAttribute, value: str
    ) -> Game:
        """
        Delete a game using a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
        Returns:
            The deleted game.
        """
        try:
            game = await self.get_game_by_attribute(attribute, value)
            await self.session.delete(game)
            await self.session.commit()

            return game
        except NoResultFound:
            raise game_not_found
        except MultipleResultsFound:
            raise multiple_games_found
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
            raise e

    async def get_games(self, offset: int = 0, limit: int = 100):
        """
        Get all games.
        Args:
            offset: The number of users to skip.
            limit: The maximum number of users to return.
        Returns:
            The list of games.
        """
        try:
            total_count_query = select(func.count()).select_from(Game)
            total_count_response = await self.session.execute(total_count_query)
            total_count: int = total_count_response.scalar_one()

            games_query = select(Game).offset(offset).limit(limit)
            games_response = await self.session.execute(games_query)
            games = games_response.scalars().all()

            return games, total_count
        except NoResultFound:
            raise game_not_found
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
            raise e

    async def ensure_game_exists(self, player: Player) -> Game:
        """
        Ensures a game exists.

        This method checks if a game exists for a player. If not, it creates a new game.
        Args:
            player: The player to ensure the game for.
        Returns:
            The game.
        """
        try:
            game = await self.get_game_by_attribute(
                GameAttribute.PLAYER_ID, str(player.id)
            )
        except HTTPException as e:
            if e.status_code == status.HTTP_404_NOT_FOUND:
                game = await self.create_new_game(player)
            else:
                raise e
        return game


class GameService(GameServiceBase):
    """
    Class for game-related services.

    Attributes:
        session: The database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

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

    async def start_game(self, player_id: UUID) -> Game:
        """
        Starts a new game.
        Args:
            player_id: The id of the player to start the game for.
        Returns:
            The game.
        """

        player_service = PlayerService(self.session)

        player: Player = await player_service.get_player_by_attribute(
            PlayerAttribute.ID, str(player_id)
        )
        game: Game = await self.ensure_game_exists(player)
        started_game = await self._construct_word_progress(
            await self._get_random_word(await self._clear_game(game))
        )
        logger.info(f"Started game for player {player.id}")
        updated_game: Game = await self.update_game_by_attribute(
            GameAttribute.PLAYER_ID, str(player.id), started_game
        )
        logger.debug(f"Updated game for player {player.id}")
        return updated_game

    async def end_game(self, player_id: UUID) -> Game:
        """
        Ends the game.
        Args:
            player_id: The id of the player to end the game for.
        Returns:
            The game.
        """
        game: Game = await self.get_game_by_attribute(
            GameAttribute.PLAYER_ID, str(player_id)
        )
        ended_game = await self._clear_game(game)
        logger.info(f"Ended game for player {player_id}")
        return ended_game

    async def continue_game(self, player_id: UUID) -> Game:
        """
        Continues the game.
        Args:
            player_id: The id of the player to continue the game for.
        Returns:
            The game.
        """
        started_game: Game = await self.start_game(player_id)
        logger.info(f"Continued game for player {player_id}")
        updated_game: Game = await self.update_game_by_attribute(
            GameAttribute.PLAYER_ID, str(player_id), started_game
        )
        logger.debug(f"Updated game for player {player_id}")
        return updated_game

    async def update_game_state(self, game_id: UUID, character: str) -> Game:
        """
        Updates the game state.
        Args:
            game_id: The id of the game to update the state for.
            character: The guessed character.
        Returns:
            The game.
        """
        game: Game = await self.get_game_by_attribute(GameAttribute.ID, str(game_id))
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
        updated_game: Game = await self.update_game_by_attribute(
            GameAttribute.ID, str(game_id), game
        )
        logger.debug(f"Updated game for game {game.id}")
        return updated_game
