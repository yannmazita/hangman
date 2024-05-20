import asyncio
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
            logger.debug(f"Attempting to create game for player: {player.id}")
            query = select(Game).where(Game.player_id == player.id)
            response = await self.session.execute(query)
            existing_game: Game | None = response.scalar_one_or_none()

            if existing_game:
                logger.warning(f"Game already exists for player: {player.id}")
                raise game_already_exists

            new_game = Game(
                id=uuid4(),
                player_id=player.id,
            )
            db_game = Game.model_validate(new_game)

            logger.debug(f"Adding new game to session: {db_game}")
            self.session.add(db_game)

            logger.debug("Committing session")
            await self.session.commit()

            logger.debug("Refreshing session")
            await self.session.refresh(db_game)

            logger.info(f"Game created successfully for player: {db_game.player_id}")
            return db_game

        except IntegrityError as e:
            logger.error(f"IntegrityError occurred: {e}", exc_info=False)
            raise e
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except HTTPException as e:
            logger.error(f"HTTPException occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
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
            logger.debug(f"Attempting to get game by {attribute.value}: {value}")
            query = select(Game).where(getattr(Game, attribute.value) == value)
            response = await self.session.execute(query)
            game = response.scalar_one()
            logger.info(f"Game found: {game.id}")
            return game
        except MultipleResultsFound:
            logger.error(
                f"Multiple games found for {attribute.value} = {value}", exc_info=False
            )
            raise multiple_games_found
        except NoResultFound:
            logger.warning(
                f"No game found for {attribute.value} = {value}", exc_info=False
            )
            raise game_not_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
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
            The updated user.
        """
        try:
            logger.debug(f"Attempting to update game by {attribute.value}: {value}")
            game_db: Game = await self.get_game_by_attribute(attribute, value)
            game_data = game.model_dump()
            for key, value in game_data.items():
                if key != "id":
                    setattr(game_db, key, value)
            logger.debug(f"Updating game: {game_db.id}")
            self.session.add(game_db)
            logger.debug("Committing session")
            await self.session.commit()
            logger.debug("Refreshing session")
            await self.session.refresh(game_db)
            logger.info(f"Game updated successfully: {game_db.id}")
            return game_db
        except NoResultFound:
            logger.warning(
                f"No game found for {attribute.value} = {value}", exc_info=False
            )
            raise game_not_found
        except MultipleResultsFound:
            logger.error(
                f"Multiple games found for {attribute.value} = {value}", exc_info=False
            )
            raise multiple_games_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
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
            logger.debug(f"Attempting to delete game: {game.id}")
            await self.session.delete(game)
            await self.session.commit()
            logger.info(f"User deleted successfully: {game.id}")
            return game
        except NoResultFound:
            logger.warning(f"No game found to delete: {game.id}", exc_info=False)
            raise game_not_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
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
            logger.debug(f"Attempting to delete game by {attribute.value}: {value}")
            game = await self.get_game_by_attribute(attribute, value)
            await self.session.delete(game)
            await self.session.commit()
            logger.info(f"Game deleted successfully: {game.id}")
            return game
        except NoResultFound:
            logger.warning(
                f"No game found for {attribute.value} = {value}", exc_info=False
            )
            raise game_not_found
        except MultipleResultsFound:
            logger.error(
                f"Multiple games found for {attribute.value} = {value}", exc_info=False
            )
            raise multiple_games_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
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
            logger.debug(f"Fetching games with offset: {offset}, limit: {limit}")
            total_count_query = select(func.count()).select_from(Game)
            total_count_response = await self.session.execute(total_count_query)
            total_count: int = total_count_response.scalar_one()

            games_query = select(Game).offset(offset).limit(limit)
            games_response = await self.session.execute(games_query)
            games = games_response.scalars().all()
            logger.info(f"Fetched {len(games)} games")
            return games, total_count
        except NoResultFound:
            logger.warning("No games found", exc_info=False)
            raise game_not_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
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

    async def get_random_word(self, player: Player) -> None:
        """
        Gets a random word from the Internet.

        This method queries random-word-api to get random words from.

        Args:
            player: The player to get the word for.
        """
        word_to_guess: str = ""

        try:
            logger.debug("Attempting to get random word")
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://random-word-api.herokuapp.com/word?number=1"
                ) as response:
                    response = await response.json()
            while len(response[0]) > MAX_WORD_LENGTH:
                logger.debug("Word too long, retrying")
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://random-word-api.herokuapp.com/word?number=1"
                    ) as response:
                        response = await response.json()
            word_to_guess = response[0]
            logger.info(f"Random word fetched: {word_to_guess}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error fetching random word: {e}", exc_info=False)
            word_to_guess = (
                "computer"  # very quick fix, need to integrate local word source
            )
            logger.warning(f"Using default word: {word_to_guess}")
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            word_to_guess = "computer"
            logger.warning(f"Using default word: {word_to_guess}")

        game: Game = await self.ensure_game_exists(player)
        await self.update_game_by_attribute(
            GameAttribute.PLAYER_ID, str(player.id), Game(word_to_guess=word_to_guess)
        )
        logger.debug(f"Word saved to game: {game.id}")

    async def construct_word_progress(self, player: Player) -> None:
        """
        Contructs the word in its current state of discovery.

        Only the correctly guessed letters are present. Other letters are replaced with '*'.

        Args:
            player: The player to construct the word progress for.
        """

        game: Game = await self.ensure_game_exists(player)

        if not game.word_progress:
            logger.debug("Initializing word progress")
            word_progress = "*" * len(game.word_to_guess)
            await self.update_game_by_attribute(
                GameAttribute.PLAYER_ID,
                str(player.id),
                Game(word_progress=word_progress),
            )
        else:
            logger.debug("Updating word progress")
            word_progress_split: list[str] = list(game.word_progress)
            for pos in game.guessed_positions:
                word_progress_split[pos] = game.word_to_guess[pos]
            word_progress = "".join(word_progress_split)
            await self.update_game_by_attribute(
                GameAttribute.PLAYER_ID,
                str(player.id),
                Game(word_progress=word_progress),
            )
        logger.debug(f"Word progress updated: {game.word_progress}")

    async def update_guessed_positions(self, player: Player, character: str) -> None:
        """
        Updates the positions of guessed characters.

        After updating the guessed_positions list this method calls construct_word_progress() and
        updates tries_left.

        Args:
            player: The player to update the guessed positions for.
            character: The guessed character.
        """

        game: Game = await self.ensure_game_exists(player)
        guessed_positions = game.guessed_positions
        guessed_corretly: bool = False

        logger.debug(f"Updating guessed positions for character: {character}")
        for pos, car in enumerate(game.word_to_guess):
            if character == car:
                guessed_positions.append(pos)
                await self.update_game_by_attribute(
                    GameAttribute.PLAYER_ID,
                    str(player.id),
                    Game(guessed_positions=guessed_positions),
                )
                guessed_corretly = True
        logger.debug(f"Guessed positions updated: {game.guessed_positions}")
        await self.construct_word_progress(player)

        if not guessed_corretly:
            logger.debug("Character not found in word")
            tries_left = game.tries_left
            await self.update_game_by_attribute(
                GameAttribute.PLAYER_ID, str(player.id), Game(tries_left=tries_left - 1)
            )
        logger.debug(f"Tries left updated: {game.tries_left}")

    async def update_guessed_letters(self, player: Player, character: str) -> None:
        """
        Updates the guessed letters list.

        This method appends the guessed character to the guessed_letters list.
        Whether the character is correct or not.

        Args:
            player: The player to update the guessed letters for.
            character: The guessed character.
        """
        game: Game = await self.ensure_game_exists(player)
        if character not in game.guessed_letters:
            guessed_letters = game.guessed_letters
            guessed_letters.append(character)
            await self.update_game_by_attribute(
                GameAttribute.PLAYER_ID,
                str(player.id),
                Game(guessed_letters=guessed_letters),
            )

    async def update_game_status(self, player: Player) -> None:
        """
        Updates the game status.

        Args:
            player: The player to update the game status for.
        """

        game: Game = await self.ensure_game_exists(player)

        if game.game_status == 0:
            if game.tries_left == 0:
                await self.update_game_by_attribute(
                    GameAttribute.PLAYER_ID, str(player.id), Game(game_status=-1)
                )
            elif game.word_to_guess == game.word_progress:
                await self.update_game_by_attribute(
                    GameAttribute.PLAYER_ID, str(player.id), Game(game_status=1)
                )
                successful_guesses = game.successful_guesses
                await self.update_game_by_attribute(
                    GameAttribute.PLAYER_ID,
                    str(player.id),
                    Game(successful_guesses=successful_guesses + 1),
                )
            else:
                await self.update_game_by_attribute(
                    GameAttribute.PLAYER_ID, str(player.id), Game(game_status=0)
                )

    async def clear_game(self, player_id: UUID) -> None:
        """
        Clears the game.
        Args:
            player_id: The id of the player to clear the game for.
        """
        player_service = PlayerService(self.session)
        player: Player = await player_service.get_player_by_attribute(
            PlayerAttribute.ID, str(player_id)
        )
        await self.ensure_game_exists(player)

        clean_game = Game(
            word_to_guess="",
            word_progress="",
            guessed_positions=[],
            guessed_letters=[],
            tries_left=MAX_TRIES,
            game_status=0,
        )
        await self.update_game_by_attribute(
            GameAttribute.PLAYER_ID, str(player.id), clean_game
        )

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
        await self.ensure_game_exists(player)
        await self.clear_game(player_id)

        await self.get_random_word(player)
        await self.construct_word_progress(player)
        game: Game = await self.ensure_game_exists(player)
        return game

    async def continue_game(self, player_id: UUID) -> Game:
        """
        Continues the game.
        Args:
            player_id: The id of the player to continue the game for.
        Returns:
            The game.
        """
        player_service = PlayerService(self.session)
        player: Player = await player_service.get_player_by_attribute(
            PlayerAttribute.ID, str(player_id)
        )
        await self.clear_game(player_id)
        await self.start_game(player_id)
        game: Game = await self.ensure_game_exists(player)
        return game

    async def update_game_state(self, player_id: UUID, character: str) -> Game:
        """
        Updates the game state.
        Args:
            player: The player to update the game state for.
            character: The guessed character.
        Returns:
            The game.
        """
        player_service = PlayerService(self.session)
        player: Player = await player_service.get_player_by_attribute(
            PlayerAttribute.ID, str(player_id)
        )
        game: Game = await self.ensure_game_exists(player)
        if game.tries_left == 0:
            raise GameOver(player.id)
        await self.update_guessed_positions(player, character)
        await self.update_guessed_letters(player, character)
        await self.update_game_status(player)
        game: Game = await self.ensure_game_exists(player)
        return game
