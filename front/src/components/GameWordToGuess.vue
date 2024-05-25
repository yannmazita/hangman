<template>
    <div id="game-word-to-guess-container" class="flex justify-center my-4">
        <div :id="`game-word-to-guess-char-${char}`" v-for="(char, index) in wordProgress" :key="index"
            class="kbd text-white bg-base-300 m-0.5">
            {{ char }}
        </div>
    </div>
</template>
<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useAppStore } from '@/stores/app.ts';

const appStore = useAppStore();
const { game } = storeToRefs(appStore);

const wordProgress = computed(() => {
    return game.value.word_progress?.split("");
});

</script>
