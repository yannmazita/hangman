import { defineStore } from 'pinia'
import { ref, reactive, Ref } from 'vue'
import { useClientStore } from '@/stores/client.ts';
import { useAuthenticationStore } from '@/stores/authentication.ts';
import { Game, Player, ServerStats } from '@/interfaces.ts';
import axios from 'axios';
import { AxiosResponse, AxiosError } from 'axios';

export const useAppStore = defineStore('app', () => {
    const clientStore = useClientStore();
    const authenticationStore = useAuthenticationStore();
    const serverStats: ServerStats = reactive({
        active_users: 0,
    });
    const gameStarted: Ref<boolean> = ref(false); // The game has started.
    const gamePaused: Ref<boolean> = ref(false); // The game has been paused.
    const game: Game = reactive({
        word_progress: '',
        guessed_letters: [],
        tries_left: 0,
        max_tries: 0,
        successful_guesses: 0,
        game_status: 0,
    });
    const player: Player = reactive({
        id: null,
        username: null,
        playername: `Player${Math.floor(Math.random() * 1000)}`,
        points: 0,
        games_played: 0,
        games_won: 0,
    });

    async function createPlayer(playername: string) {
        try {
            const response: AxiosResponse = await axios.post(`${import.meta.env.VITE_API_URL}/players/`,
                {
                    "playername": playername,
                },
                {
                    headers: {
                        accept: 'application/json',
                        Authorization: `Bearer ${authenticationStore.tokenData.access_token}`,
                    }
                }
            );
            Object.assign(player, response.data);
        }
        catch (error) {
            console.error('Failed to create player:', error);
        }
    }

    async function getOwnPlayer() {
        try {
            const response: AxiosResponse = await axios.get(
                `${import.meta.env.VITE_API_URL}/players/me`,
                {
                    headers: {
                        accept: 'application/json',
                        Authorization: `Bearer ${authenticationStore.tokenData.access_token}`,
                    }
                }
            );
            Object.assign(player, response.data);
        }
        catch (error) {
            //console.log(error);
            //throw error; // Rethrow the error to the caller.
            // only works when it's a js error, not an axios error?
            console.error('Failed to get own player:', error);
        }
    }

    const clearPlayer = function() {
        player.id = null;
        player.username = null;
        player.playername = `Player${Math.floor(Math.random() * 1000)}`;
        player.points = 0;
        player.games_played = 0;
        player.games_won = 0;
    }

    async function startGame() {
        gameStarted.value = true;
        await getOwnPlayer();
        if (player.id === null) {
            await createPlayer(player.playername);
        }

        try {
            const response: AxiosResponse = await axios.post(`${import.meta.env.VITE_API_URL}/game/start/player_id/${player.id}`,
                {
                    headers: {
                        accept: 'application/json',
                        Authorization: `Bearer ${authenticationStore.tokenData.access_token}`,
                    }
                }
            );
            Object.assign(game, response.data);
        }
        catch (error) {
            console.error('Failed to start game:', error);
        }
    }

    async function endGame() {
        gameStarted.value = false;
        //userStore.disconnectSocket();
        //userStore.resetSocket();
    }

    async function guessCharacter(character: string) {
        try {
            const response: AxiosResponse = await axios.post(`${import.meta.env.VITE_API_URL}/game/guess_character/player_id/${player.id}/`,
                {
                    "character": character,
                },
                {
                    headers: {
                        accept: 'application/json',
                        Authorization: `Bearer ${authenticationStore.tokenData.access_token}`,
                    }
                }
            );
            Object.assign(game, response.data);
        }
        catch (error) {
            console.error('Failed to guess letter:', error);
        }

    }

    async function continueGame() {
        try {
            const response: AxiosResponse = await axios.post(`${import.meta.env.VITE_API_URL}/game/continue/player_id/${player.id}`,
                {
                    headers: {
                        accept: 'application/json',
                        Authorization: `Bearer ${authenticationStore.tokenData.access_token}`,
                    }
                }
            );
            Object.assign(game, response.data);
        }
        catch (error) {
            console.error('Failed to continue game:', error);

        }
    }

    async function getServerStats() {
        clientStore.sendSocketMessage(JSON.stringify({
            action: 'server_stats',
        }));
    };

    return {
        startGame,
        endGame,
        guessCharacter,
        continueGame,
        gameStarted,
        gamePaused,
        createPlayer,
        getOwnPlayer,
        clearPlayer,
        player,
        game,
        serverStats,
        getServerStats,
    }
})

