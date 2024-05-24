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
            The updated user.
        """
        try:
            game_db: Game = await self.get_game_by_attribute(attribute, value)
            logger.debug(f"Found game: {game_db}")

            game_data = game.model_dump()
            for key, val in game_data.items():
                if key != "id":
                    setattr(game_db, key, val)
                    logger.debug(f"Set {key} to {val}")

            self.session.add(game_db)
            logger.debug(f"Added game to session: {game_db}")

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

    async def get_random_word(self, player: Player) -> None:
        """
        Gets a random word from the Internet.

        This method queries random-word-api to get random words from.

        Args:
            player: The player to get the word for.
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

        game: Game = await self.ensure_game_exists(player)

        await self.update_game_by_attribute(
            GameAttribute.PLAYER_ID, str(player.id), Game(word_to_guess=word_to_guess)
        )
        logger.debug(f"Got random word for player {player.id}")
        logger.debug(f"Word to guess: {word_to_guess}")

    async def construct_word_progress(self, player: Player) -> None:
        """
        Contructs the word in its current state of discovery.

        Only the correctly guessed letters are present. Other letters are replaced with '*'.

        Args:
            player: The player to construct the word progress for.
        """
        game: Game = await self.ensure_game_exists(player)

        if not game.word_progress:
            word_progress = "*" * len(game.word_to_guess)
            await self.update_game_by_attribute(
                GameAttribute.PLAYER_ID,
                str(player.id),
                Game(word_progress=word_progress),
            )
        else:
            word_progress_split: list[str] = list(game.word_progress)
            for pos in game.guessed_positions:
                word_progress_split[pos] = game.word_to_guess[pos]
            word_progress = "".join(word_progress_split)
            await self.update_game_by_attribute(
                GameAttribute.PLAYER_ID,
                str(player.id),
                Game(word_progress=word_progress),
            )
        logger.debug(f"Constructed word progress for player {player.id}")

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

        for pos, car in enumerate(game.word_to_guess):
            if character == car:
                guessed_positions.append(pos)
                await self.update_game_by_attribute(
                    GameAttribute.PLAYER_ID,
                    str(player.id),
                    Game(guessed_positions=guessed_positions),
                )
                guessed_corretly = True

        await self.construct_word_progress(player)

        if not guessed_corretly:
            tries_left = game.tries_left
            await self.update_game_by_attribute(
                GameAttribute.PLAYER_ID, str(player.id), Game(tries_left=tries_left - 1)
            )
        logger.debug(f"Updated guessed positions for player {player.id}")

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
        logger.debug(f"Updated guessed letters for player {player.id}")

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
        logger.debug(f"Updated game status for player {player.id}")

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
        logger.debug(f"Cleared game for player {player.id}")

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
        logger.info(f"Started game for player {player.id}")
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
        logger.info(f"Continued game for player {player.id}")
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
        logger.info(f"Updated game state for player {player.id}")
        return game
