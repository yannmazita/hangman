<template>
    <div class="grid grid-rows-6 h-[calc(100vh-48px)]">
        <div class="row-start-1 row-end-2">
            <StatusBar class="" />
        </div>
        <div class="row-start-2 row-end-3">
        </div>
        <div class="row-start-3 row-end-4">
        </div>
        <div class="row-start-4 row-end-7 flex justify-center items-end">
            <div>
                <WordToGuess></WordToGuess>
                <CharInput></CharInput>
            </div>
        </div>
    </div>
</template>
<script setup lang="ts">
import StatusBar from '@/components/GameStatusBar.vue';
import WordToGuess from '@/components/GameWordToGuess.vue';
import CharInput from '@/components/GameCharacterInput.vue';
import AppButton from '@/components/AppButton.vue';
import { useMenuStore } from '@/stores/menu.ts';
import { useGameStore } from '@/stores/game.ts';

const menuStore = useMenuStore();
const gameStore = useGameStore();

const quitGame = function () {
    gameStore.endGame();
    menuStore.resetChoices();
};

const pauseGame = function () {
    //gameStore.gamePaused = true;
    menuStore.resetChoices();
};
</script>
