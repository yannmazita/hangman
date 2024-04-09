export interface TokenData {
    access_token: string | null,
    token_type: string | null,
}

export interface User {
    id: string | null,
    username: string | null,
    player_id: string | null,
}

export interface ServerStats {
    active_players: number,
}

export interface Player {
    id: string | null,
    username: string | null,
    playername: string,
    points: number,
    games_played: number,
    games_won: number,
}

export interface Game {
    word_progress: string | null,
    guessed_letters: string[],
    tries_left: number,
    max_tries: number,
    successful_guesses: number,
    game_status: number,
}
