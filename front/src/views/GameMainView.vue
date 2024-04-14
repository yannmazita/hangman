<template>
    <div id="game-main-view-container" class="flex flex-col h-full">
        <StatusBar></StatusBar>
        <Continue></Continue>
        <div id="game-main-view" class="flex flex-col h-full">
            <div id="game-word-container" class="mt-auto w-full">
                <div id="game-word-keyboard" class="w-full">
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
