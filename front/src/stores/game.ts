import { defineStore } from 'pinia'
import { ref, reactive, Ref } from 'vue'
import { useUserStore } from '@/stores/user.ts';
import { useAuthenticationStore } from '@/stores/authentication.ts';
import { Game, Player, ServerStats } from '@/interfaces.ts';
import axios from 'axios';

export const useGameStore = defineStore('game', () => {
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
    const serverStats: ServerStats = reactive({
        active_players: 0,
    });
    const userStore = useUserStore();
    const authenticationStore = useAuthenticationStore();

    async function createPlayer(playername: string) {
        try {
            const response = await axios.post(`${import.meta.env.VITE_API_URL}/players/`,
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
            console.log(error);
        }
    }

    async function getOwnPlayer() {
        try {
            const response = await axios.get(
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
        if (player.id === null) {
            try {
                await getOwnPlayer();
            }
            catch (error) {
                console.log(error);
            }
        }

        try {
            await userStore.connectSocket();
            await userStore.sendSocketMessage(JSON.stringify({
                action: 'start_game',
            }));
        }
        catch (error) {
            console.log(error);
        }
    }

    const endGame = function() {
        gameStarted.value = false;
        userStore.disconnectSocket();
        userStore.resetSocket();
    }

    async function getServerStats() {
        userStore.sendSocketMessage(JSON.stringify({
            action: 'server_stats',
        }));
    };

    return {
        startGame,
        endGame,
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

