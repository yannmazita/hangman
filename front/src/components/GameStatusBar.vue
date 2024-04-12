<template>
    <div class="flex justify-between">
        <div id="guessInfo" class="relative px-2 py-1.5">
            <div id="guessInfoWords" class="absolute z-10 p-2 rounded-full font-bold text-black bg-gray-300">words</div>
            <div id="guessInfoGuesses" class="absolute left-9 top-2 z-0 ps-10 pe-3 rounded-lg bg-white text-3xl font-bold text-cyan-700">{{
                successfulGuesses
            }}</div>
        </div>
        <div id="triesInfo" class="relative p-2">
            <div id="triesInfoTriesLeft" class="z-0 pe-10 ps-3 rounded-lg bg-white text-3xl font-bold text-cyan-700">
                {{ triesLeft }}
            </div>
            <div id="triesInfoHeart" class="absolute left-12 top-1.5 z-10 p-2 rounded-full font-bold text-black bg-gray-300">💙</div>
        </div>
    </div>
</template>
<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useGameStore } from '@/stores/game.ts';

const gameStore = useGameStore();
const { game } = storeToRefs(gameStore);

const successfulGuesses = computed(() => {
    return game.value.successful_guesses;
});
const triesLeft = computed(() => {
    return game.value.tries_left;
});
</script>
