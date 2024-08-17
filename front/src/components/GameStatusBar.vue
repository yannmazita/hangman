<template>
    <div id="game-status-bar-container" class="flex flex-row justify-evenly my-4">
        <div id="game-status-bar-guess-info-container" class="flex">
            <div id="game-status-bar-guesses" class="bg-white rounded h-fit p-1 text-3xl font-bold text-cyan-700">
                <span id="game-status-bar-guesses-icon" class="mx-1 text-2xl">⭐</span>
                <span id="game-status-bar-guesses-number" class="mx-1">{{ successfulGuesses }}</span>
            </div>
        </div>
        <div id="game-status-bar-action-buttons-container" class="p-1 bg-white rounded h-fit">
            <button id="game-status-bar-action-buttons-pause" @click="pauseGame" class="p-1.5">
                ⏸️
            </button>
            <button id="game-status-bar-action-buttons-quit" @click="quitGame" class="p-1.5">
                ↩️
            </button>
        </div>
        <div id="game-status-bar-tries-container" class="flex">
            <div id="game-status-bar-tries" class="bg-white rounded h-fit p-1 text-3xl font-bold text-cyan-700">
                <span id="game-status-bar-tries-number" class="mx-1">{{ triesLeft }}</span>
                <span id="game-status-bar-tries-icon" class="mx-1 text-2xl">💙</span>
            </div>
        </div>
    </div>
</template>
<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useAppStore } from '@/stores/app.ts';
import { useMenuStore } from '@/stores/menu.ts';
import { PageType } from '@/enums.ts';

const appStore = useAppStore();
const menuStore = useMenuStore();
const { game } = storeToRefs(appStore);

const successfulGuesses = computed(() => {
    return game.value.successful_guesses;
});
const triesLeft = computed(() => {
    return game.value.tries_left;
});

function quitGame(): void {
    appStore.endGame();
    menuStore.setCurrentPage(PageType.SELECT_SCREEN);
};
function pauseGame(): void {
    //appStore.gamePaused = true;
    menuStore.setCurrentPage(PageType.SELECT_SCREEN);
};
</script>
