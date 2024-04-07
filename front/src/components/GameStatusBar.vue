<template>
    <div class="mx-3 my-5 grid grid-cols-12">
        <div class="w-fit h-fit z-10 p-2 rounded-full font-bold text-amber-600 bg-yellow-300 shadow-lg shadow-gray-400">words</div>
        <div class="flex items-end col-start-2 ps-10 pe-3 w-fit h-fit z-0 rounded-lg bg-white text-3xl font-bold text-cyan-700 shadow-lg shadow-gray-400">
            {{ successfulGuesses
            }}
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
</script>
