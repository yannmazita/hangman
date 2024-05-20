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
                <AppButton @click="menuStore.setCurrentPage(PageType.SETTINGS)">{{ 'Settings' }}</AppButton>
            </li>
        </div>
    </menu>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useMenuStore } from '@/stores/menu.js';
import { useAppStore } from '@/stores/app.ts';
import { useAuthenticationStore } from '@/stores/authentication.js';
import { PageType } from '@/enums.ts';
import AppButton from '@/components/AppButton.vue';

const menuStore = useMenuStore();
const appStore = useAppStore();
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
        menuStore.setCurrentPage(PageType.AUTH);
    }
    else {
        authStore.logoutUser();
        appStore.clearPlayer();
    }
};

const gameState = computed(() => {
    if (appStore.gameStarted) {
        return 'Continue';
    }
    else {
        return 'Play';
    }
});

const gameStateChoice = function () {
    if (appStore.gameStarted) {
        menuStore.setCurrentPage(PageType.GAME);
    }
    else {
        menuStore.setCurrentPage(PageType.GAME);
        appStore.startGame();
    }
};

onMounted(() => {
    menuStore.setCurrentPage(PageType.SELECT_SCREEN);
});
</script>
