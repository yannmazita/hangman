import asyncio
import requests
from uuid import uuid4
from fastapi import HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from app.game.config import MAX_WORD_LENGTH, MAX_TRIES
from app.game.exceptions import (
    game_already_exists,
    game_not_found,
    multiple_games_found,
    GameOver,
)
from app.game.models import Game
from app.game.schemas import GameAttribute
from app.players.models import Player


class GameServiceBase:
    """
    Base class for game-related services.

    Attributes:
        session: The database session.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_new_game(self, player: Player) -> Game:
        """
        Creates a new game.
        Args:
            player: The player to create the game for.
        Returns:
            The created game.
        """
        try:
            self.session.exec(select(Game).where(Game.player_id == player.id)).one()
            raise game_already_exists
        except NoResultFound:
            pass

        new_game = Game(
            player_id=player.id,
        )
        db_game = Game.model_validate(new_game)
        self.session.add(db_game)
        self.session.commit()
        self.session.refresh(db_game)

        return db_game

    def get_game(self, player: Player) -> Game:
        """
        Retrieve a player's game from the database.

        Args:
            player: The player to get the game for.
        Returns:
            The game.
        """
        try:
            game = self.session.exec(
                select(Game).where(Game.player_id == player.id)
            ).one()
            return game
        except NoResultFound:
            raise game_not_found
        except MultipleResultsFound:
            raise multiple_games_found

    def get_game_by_attribute(self, attribute: GameAttribute, value: str) -> Game:
        """
        Gets a game by a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value of the attribute.
        Returns:
            The game.
        """
        try:
            game = self.session.exec(
                select(Game).where(getattr(Game, attribute.value) == value)
            ).one()
        except MultipleResultsFound:
            raise multiple_games_found
        except NoResultFound:
            raise game_not_found
        return game

    def update_game(self, player: Player, game: Game) -> Game:
        """
        Update a player's game in the database.

        Args:
            player: The player to update the game for.
            game: The updated player game.
        Returns:
            The updated game.
        """
        try:
            db_game = self.get_game(player)
            game_data = game.model_dump()
            for key, value in game_data.items():
                setattr(db_game, key, value)
            self.session.add(db_game)
            self.session.commit()
            self.session.refresh(db_game)
        except NoResultFound:
            raise game_not_found
        except MultipleResultsFound:
            raise multiple_games_found

        return db_game

    def update_game_by_attribute(
        self, attribute: GameAttribute, value: str, game: Game
    ) -> Game:
        """
        Updates a game by a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value of the attribute.
            game: The game to update.
        Returns:
            The updated game.
        """
        try:
            game_db = self.get_game_by_attribute(attribute, value)
            game_data = game.model_dump()
            for key, value in game_data.items():
                setattr(game_db, key, value)
            self.session.add(game_db)
            self.session.commit()
            self.session.refresh(game_db)
        except NoResultFound:
            raise game_not_found
        except MultipleResultsFound:
            raise multiple_games_found

        return game_db

    def delete_game(self, game: Game) -> None:
        """
        Deletes a game.
        Args:
            game: The game to delete.
        """
        try:
            self.session.delete(game)
            self.session.commit()
        except NoResultFound:
            raise game_not_found

    def delete_game_by_attribute(self, attribute: GameAttribute, value: str) -> None:
        """
        Deletes a game by a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value of the attribute.
        """
        try:
            game = self.get_game_by_attribute(attribute, value)
            self.session.delete(game)
            self.session.commit()
        except NoResultFound:
            raise game_not_found
        except MultipleResultsFound:
            raise multiple_games_found

    def get_games(self, offset: int = 0, limit: int = 100):
        """
        Gets all games.
        Args:
            offset: The offset.
            limit: The limit.
        Returns:
            The games.
        """
        games = self.session.exec(select(Game).offset(offset).limit(limit)).all()
        return games

    def ensure_game_exists(self, player: Player) -> Game:
        """
        Ensures a game exists.
        Args:
            player: The player to ensure the game for.
        Returns:
            The game.
        """
        try:
            game = self.get_game(player)
        except HTTPException as e:
            if e.status_code == status.HTTP_404_NOT_FOUND:
                game = self.create_new_game(player)
            else:
                raise e
        return game


class GameService(GameServiceBase):
    """
    Class for game-related services.

    Attributes:
        session: The database session.
    """

    def __init__(self, session: Session) -> None:
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
            response = await asyncio.to_thread(
                requests.get, "https://random-word-api.herokuapp.com/word?number=1"
            )
            while len(response.json()[0]) > MAX_WORD_LENGTH:
                response = await asyncio.to_thread(
                    requests.get, "https://random-word-api.herokuapp.com/word?number=1"
                )
            word_to_guess = response.json()[0]
        except requests.exceptions.ConnectionError as e:
            word_to_guess = (
                "computer"  # very quick fix, need to integrate local word source
            )

        game: Game = self.ensure_game_exists(player)
        self.update_game(player, Game(word_to_guess=word_to_guess))

    def construct_word_progress(self, player: Player) -> None:
        """
        Contructs the word in its current state of discovery.

        Only the correctly guessed letters are present. Other letters are replaced with '*'.

        Args:
            player: The player to construct the word progress for.
        """

        game: Game = self.ensure_game_exists(player)

        if not game.word_progress:
            word_progress = "*" * len(game.word_to_guess)
            self.update_game(player, Game(word_progress=word_progress))
        else:
            word_progress_split: list[str] = list(game.word_progress)
            for pos in game.guessed_positions:
                word_progress_split[pos] = game.word_to_guess[pos]
            word_progress = "".join(word_progress_split)
            self.update_game(player, Game(word_progress=word_progress))

    def update_guessed_positions(self, player: Player, character: str) -> None:
        """
        Updates the positions of guessed characters.

        After updating the guessed_positions list this method calls construct_word_progress() and
        updates tries_left.

        Args:
            player: The player to update the guessed positions for.
            character: The guessed character.
        """

        game: Game = self.ensure_game_exists(player)
        guessed_positions = game.guessed_positions
        guessed_corretly: bool = False

        for pos, car in enumerate(game.word_to_guess):
            if character == car:
                guessed_positions.append(pos)
                self.update_game(player, Game(guessed_positions=guessed_positions))
                guessed_corretly = True
        self.construct_word_progress(player)

        if not guessed_corretly:
            tries_left = game.tries_left
            self.update_game(player, Game(tries_left=tries_left - 1))

    def update_guessed_letters(self, player: Player, character: str) -> None:
        """
        Updates the guessed letters list.

        This method appends the guessed character to the guessed_letters list.
        Whether the character is correct or not.

        Args:
            player: The player to update the guessed letters for.
            character: The guessed character.
        """
        game: Game = self.ensure_game_exists(player)
        if character not in game.guessed_letters:
            guessed_letters = game.guessed_letters
            guessed_letters.append(character)
            self.update_game(player, Game(guessed_letters=guessed_letters))

    def update_game_status(self, player: Player) -> None:
        """
        Updates the game status.

        Args:
            player: The player to update the game status for.
        """

        game: Game = self.ensure_game_exists(player)

        if game.game_status == 0:
            if game.tries_left == 0:
                self.update_game(player, Game(game_status=-1))
            elif game.word_to_guess == game.word_progress:
                self.update_game(player, Game(game_status=1))
                successful_guesses = game.successful_guesses
                self.update_game(
                    player, Game(successful_guesses=successful_guesses + 1)
                )
            else:
                self.update_game(player, Game(game_status=0))

    def clear_game(self, player: Player) -> None:
        """
        Clears the game.
        Args:
            player: The player to clear the game for.
        """
        game: Game = self.ensure_game_exists(player)
        self.update_game(player, Game(word_to_guess=""))
        self.update_game(player, Game(word_progress=""))
        self.update_game(player, Game(guessed_positions=[]))
        self.update_game(player, Game(guessed_letters=[]))
        self.update_game(player, Game(tries_left=MAX_TRIES))
        self.update_game(player, Game(game_status=0))

    async def start_game(self, player: Player) -> None:
        """
        Starts a new game.
        Args:
            player: The player to start the game for.
        """
        game: Game = self.ensure_game_exists(player)
        self.clear_game(player)

        await self.get_random_word(player)
        self.construct_word_progress(player)

    async def continue_game(self, player: Player) -> None:
        """
        Continues the game.
        Args:
            player: The player to continue the game for.
        """
        self.clear_game(player)
        await self.start_game(player)

    def update_game_state(self, player: Player, character: str) -> None:
        """
        Updates the game state.
        Args:
            player: The player to update the game state for.
            character: The guessed character.
        """
        game: Game = self.ensure_game_exists(player)
        if game.tries_left == 0:
            raise GameOver(player.id)
        self.update_guessed_positions(player, character)
        self.update_guessed_letters(player, character)
        self.update_game_status(player)
