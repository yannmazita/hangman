<template>
    <div class="grid grid-cols-12">
        <span id="guessInfo" class="col-start-1 relative px-2 py-1.5">
            <span id="guessInfoWords" class="absolute z-10 p-2 rounded-full font-bold text-black bg-gray-300">words</span>
            <span id="guessInfoGuesses" class="absolute left-9 top-2 z-0 ps-10 pe-3 rounded-lg bg-white text-3xl font-bold text-cyan-700">{{
                successfulGuesses
            }}</span>
        </span>
        <span id="triesInfo" class="col-start-10 relative p-2">
            <span id="triesInfoTriesLeft" class="absolute z-0 pe-10 ps-3 rounded-lg bg-white text-3xl font-bold text-cyan-700">
                {{ triesLeft }}
            </span>
            <span id="triesInfoHeart" class="absolute left-12 top-1.5 z-10 p-2 rounded-full font-bold text-black bg-gray-300">💙</span>
        </span>
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
