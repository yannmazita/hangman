<template>
    <div class="flex flex-col h-full">
        <StatusBar class="mb-8"></StatusBar>
        <Continue></Continue>
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
import Continue from '@/components/GameContinueScreen.vue';
</script>
