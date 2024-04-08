<template>
    <div class="mx-3 my-5 grid grid-cols-12">
        <div class="w-fit h-fit z-10 p-2 rounded-full font-bold text-black bg-gray-300">
            words</div>
        <div
            class="flex items-end col-start-2 ps-10 pe-3 w-fit h-fit z-0 rounded-lg bg-white text-3xl font-bold text-cyan-700">
            {{ successfulGuesses }}
        </div>
        <div
            class="flex justify-center items-center col-start-10 w-fit h-fit pe-10 ps-3 text-3xl font-bold text-cyan-700 bg-white rounded-lg">
            {{ triesLeft }}
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
const maxTries = computed(() => {
    return game.value.max_tries;
});
</script>
