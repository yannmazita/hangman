from app.exceptions import NoGameInstance, GameOver

from uuid import UUID
import asyncio
import requests


class Game:
    """
    The game.
    
    Attributes:
        MAX_TRIES: The maximum number of tries.
        MAX_WORD_LENGTH: The maximum word length.

        word_to_guess: The word to guess.
        word_progress: The word in its current state of discovery.
        guessed_positions: The positions of guessed characters.
        guessed_letters: The guessed letters.
        tries_left: The number of tries left.
        successful_guesses: The number of successful guesses.
        game_status: The status of the game. 0: Not decided, 1: Won, -1: Lost.
    """
    MAX_TRIES: int = 5
    MAX_WORD_LENGTH: int = 8

    def __init__(self):
        """
        Initializes the game.
        """
        self.word_to_guess: str = ""
        self.word_progress: str = ""
        self.guessed_positions: list[int] = []
        self.guessed_letters: list[str] = []
        self.tries_left: int = Game.MAX_TRIES
        self.successful_guesses: int = 0
        self.game_status: int = 0


class Games:
    """
    The games manager.
    """

    def __init__(self):
        self.games: dict[UUID, Game] = {}

    def create_game_instance(self, user_id: UUID) -> None:
        """
        Creates a game instance for a user.

        Args:
            user_id: The id of the user.
        """
        self.games[user_id] = Game()

    def remove_game_instance(self, user_id: UUID) -> None:
        """
        Removes a game instance of a user.

        Args:
            user_id: The id of the user.
        """
        try:
            self.games.pop(user_id)
        except KeyError:
            raise NoGameInstance(user_id)

    def get_game_instance(self, user_id: UUID) -> Game:
        """
        Gets the game instance of a user.

        Args:
            user_id: The id of the user.

        Returns:
            The game instance of the user.
        """
        try:
            return self.games[user_id]
        except KeyError:
            raise NoGameInstance(user_id)

    async def get_random_word(self, user_id: UUID) -> None:
        """
        Gets a random word from the Internet.

        This method queries random-word-api to get random words from.

        Args:
            user_id: The id of the user.
        """

        game: Game = self.get_game_instance(user_id)

        try:
            response = await asyncio.to_thread(
                requests.get, "https://random-word-api.herokuapp.com/word?number=1"
            )
            while len(response.json()[0]) > game.MAX_WORD_LENGTH:
                response = await asyncio.to_thread(
                    requests.get, "https://random-word-api.herokuapp.com/word?number=1"
                )
            game.word_to_guess = response.json()[0]
        except requests.exceptions.ConnectionError as e:
            game.word_to_guess = (
                "computer"  # very quick fix, need to integrate local word source
            )

    def construct_word_progress(self, user_id: UUID) -> None:
        """
        Contructs the word in its current state of discovery.

        Only the correctly guessed letters are present. Other letters are replaced with '*'.

        Args:
            user_id: The id of the user.
        """

        game: Game = self.get_game_instance(user_id)

        if not game.word_progress:
            game.word_progress = "*" * len(game.word_to_guess)
        else:
            word_progress_split: list[str] = list(game.word_progress)
            for pos in game.guessed_positions:
                word_progress_split[pos] = game.word_to_guess[pos]
            game.word_progress = "".join(word_progress_split)

    def update_word_to_guess(self, user_id: UUID) -> None:
        """
        Updates the word to guess.

        Args:
            user_id: The id of the user.
        """
        game: Game = self.get_game_instance(user_id)
        game.word_to_guess = ""

    def update_guessed_positions(self, user_id: UUID, character: str) -> None:
        """
        Updates the positions of guessed characters.

        After updating the guessed_positions list this method calls construct_word_progress() and
        updates tries_left.

        Args:
            user_id: The id of the user.
            character: The guessed character.
        """

        game: Game = self.get_game_instance(user_id)
        guessed_corretly: bool = False

        for pos, car in enumerate(game.word_to_guess):
            if character == car:
                game.guessed_positions.append(pos)
                guessed_corretly = True
        self.construct_word_progress(user_id)

        if not guessed_corretly:
            game.tries_left -= 1

    def update_guessed_letters(self, user_id: UUID, character: str) -> None:
        """
        Updates the guessed letters list.

        This method appends the guessed character to the guessed_letters list.
        Whether the character is correct or not.

        Args:
            user_id: The id of the user.
            character: The guessed character.
        """
        game: Game = self.get_game_instance(user_id)
        if character not in game.guessed_letters:
            game.guessed_letters.append(character)

    def update_game_status(self, user_id: UUID) -> None:
        """
        Updates the game status.

        Args:
            user_id: The id of the user.
        """

        game: Game = self.get_game_instance(user_id)

        if game.game_status == 0:
            if game.tries_left == 0:
                game.game_status = -1
            elif game.word_to_guess == game.word_progress:
                game.game_status = 1
                game.successful_guesses += 1
            else:
                game.game_status = 0

    async def start_game(self, user_id: UUID) -> None:
        """
        Starts a new game.
        Args:
            user_id: The id of the user.
        """
        self.create_game_instance(user_id)
        await self.get_random_word(user_id)
        self.construct_word_progress(user_id)

    def update_game(self, user_id: UUID, character: str) -> None:
        """
        Updates the game.
        Args:
            user_id: The id of the user.
            character: The guessed character.
        """
        game: Game = self.get_game_instance(user_id)
        if game.tries_left == 0:
            raise GameOver(user_id)
        self.update_guessed_positions(user_id, character)
        self.update_guessed_letters(user_id, character)
        self.update_game_status(user_id)
