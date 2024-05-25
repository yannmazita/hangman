export interface TokenData {
    access_token: string | null,
    token_type: string | null,
}

export interface UserCreate {
    username: string,
    password: string,
}

export interface User {
    id: string,
    username: string,
    roles: string,
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
    id: string | null,
    word_progress: string | null,
    guessed_letters: string[],
    tries_left: number,
    max_tries: number,
    successful_guesses: number,
    game_status: number,
}

export interface ServerStats {
    active_users: number,
}
