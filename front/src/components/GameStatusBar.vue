<template>
    <div id="status-bar-container" class="flex flex-row justify-evenly">
        <div id="status-bar-guessInfo" class="flex">
            <div class="bg-white rounded h-fit p-1 text-3xl font-bold text-cyan-700">
                <span class="text-2xl">⭐</span>
                {{ successfulGuesses }}
            </div>
        </div>
        <div id="status-bar-statusButtons" class="p-1 bg-white rounded h-fit">
            <button @click="pauseGame" id="statusButtonPause" class="p-2">
                ⏸️
            </button>
            <button @click="quitGame" id="statusButtonQuit" class="z-10 p-2">
                ↩️
            </button>
        </div>
        <div id="status-bar-triesInfo" class="flex">
            <div class="bg-white rounded h-fit p-1 text-3xl font-bold text-cyan-700">
                {{ triesLeft }}
                <span class="text-2xl">💙</span>
            </div>
        </div>
    </div>
</template>
<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useGameStore } from '@/stores/game.ts';
import { useMenuStore } from '@/stores/menu.ts';

const gameStore = useGameStore();
const menuStore = useMenuStore();
const { game } = storeToRefs(gameStore);

const successfulGuesses = computed(() => {
    return game.value.successful_guesses;
});
const triesLeft = computed(() => {
    return game.value.tries_left;
});

const quitGame = function () {
    gameStore.endGame();
    menuStore.resetChoices();
};
const pauseGame = function () {
    //gameStore.gamePaused = true;
    menuStore.resetChoices();
};
</script>
