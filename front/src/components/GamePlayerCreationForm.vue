<template>
    <div class="grid grid-flow-row">
        <h3 class="flex justify-center text-4xl xs:text-5xl pb-9">
            Choose your player name
        </h3>
        <form @submit.prevent="submitForm" method="post">
            <div class="flex flex-col px-5">
                <AppInput v-model="playername" type="text" class="input input-bordered text-xl" :label="'Playername'" />
            </div>
            <div class="flex justify-center">
                <div class="grid grid-flow-row">
                    <AppButton @click="goToSelectScreen">{{ 'Select Screen' }}</AppButton>
                </div>
            </div>
        </form>
    </div>
</template>
<script setup lang="ts">
import { useGameStore } from '@/stores/game.ts';
import { useMenuStore } from '@/stores/menu.ts';
import { ref } from 'vue';
import AppButton from '@/components/AppButton.vue';
import AppInput from '@/components/AppInput.vue';

const gameStore = useGameStore();
const menuStore = useMenuStore();
const playername = ref('');

const goToSelectScreen = function () {
    //gameStore.gamePaused = true;
    menuStore.resetChoices();
};

async function submitForm() {
    gameStore.createPlayer(playername.value);
}
</script>
