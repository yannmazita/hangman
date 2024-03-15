<template>
    <div class="flex justify-center text-white text-3xl">
        {{ wordProgress }}
    </div>
</template>
<script setup lang="ts">
import { computed, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores/user.js';
import { useGameStore } from '@/stores/game.ts';

const userStore = useUserStore();
const gameStore = useGameStore();
const { socketMessage } = storeToRefs(userStore);
const { game } = storeToRefs(gameStore);

watch(socketMessage, (message) => {
    console.log('Inside GameWordToGuess, socketMessage watcher, message: ', message);
    if (message !== null) {
        console.log('Inside GameWordToGuess, socketMessage watcher, message.action: ', message.action);
        if (message.action === 'game_started') {
            console.log('Inside GameWordToGuess, socketMessage watcher, message.data: ', message.data);
            Object.assign(game.value, message.data);

            console.log(`wordProgress = ${game.value.word_progress}`);
        }
    }
});

const wordProgress = computed(() => {
    return game.value.word_progress;
});

</script>
