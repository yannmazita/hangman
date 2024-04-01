<template>
    <menu class="">
        <div class="grid grid-flow-row">
            <li class="flex justify-center">
                <AppButton @click="gameStateChoice">{{ gameState }}</AppButton>
            </li>
            <li class="flex justify-center">
                <AppButton @click="logChoice">{{ logInOut }}</AppButton>
            </li>
            <li class="flex justify-center">
                <AppButton @click="menuStore.setSettingsChoice(true)">{{ 'Settings' }}</AppButton>
            </li>
        </div>
    </menu>
</template>

<script setup lang="ts">
import AppButton from '@/components/AppButton.vue';
import { useMenuStore } from '@/stores/menu.js';
import { useGameStore } from '@/stores/game.ts';
import { useAuthenticationStore } from '@/stores/authentication.js';
import { computed } from 'vue';

const menuStore = useMenuStore();
const gameStore = useGameStore();
const authStore = useAuthenticationStore();

const logInOut = computed(() => {
    if (authStore.authenticated == false) {
        return 'Connect';
    }
    else {
        return 'Disconnect';
    }
});

const logChoice = function () {
    if (authStore.authenticated == false) {
        menuStore.setLoginChoice(true);
    }
    else {
        authStore.logoutUser();
        gameStore.clearPlayer();
    }
};

const gameState = computed(() => {
    if (gameStore.gameStarted) {
        return 'Continue';
    }
    else {
        return 'Play';
    }
});

const gameStateChoice = function () {
    if (gameStore.gameStarted) {
        menuStore.setPlayChoice(true);
    }
    else {
        menuStore.setPlayChoice(true);
        gameStore.startGame();
    }
};
</script>
