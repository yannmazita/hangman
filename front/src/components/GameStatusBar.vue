<template>
    <div class="stats shadow grid grid-cols-2 rounded-none rounded-b-xl bg-cyan-600">
        <div class="stat flex flex-col justify-evenly px-0 py-2">
            <div class="stat-title text-sm self-center text-white">Guessed words</div>
            <div class="stat-value text-secondary text-base self-center">{{ successfulGuesses }}</div>
        </div>
        <div class="stat flex flex-col justify-evenly px-0 py-2">
            <div class="stat-title text-sm self-center text-white">Score</div>
            <div class="stat-value text-base self-center">1337</div>
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
