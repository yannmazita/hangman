<template>
    <div class="flex flex-col h-full">
        <StatusBar></StatusBar>
        <div class="flex h-full">
            <div class="grid grid-cols-12 items-end">
                <div class="col-span-12">
                    <WordToGuess></WordToGuess>
                    <CharInput></CharInput>
                </div>
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
