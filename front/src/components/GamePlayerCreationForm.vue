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
import { ref } from 'vue';
import { useAppStore } from '@/stores/app.ts';
import { useMenuStore } from '@/stores/menu.ts';
import { PageType } from '@/enums.ts';
import AppButton from '@/components/AppButton.vue';
import AppInput from '@/components/AppInput.vue';

const appStore = useAppStore();
const menuStore = useMenuStore();
const playername = ref('');

function goToSelectScreen(): void {
    //appStore.gamePaused = true;
    menuStore.setCurrentPage(PageType.SELECT_SCREEN);
};

async function submitForm(): Promise<void> {
    appStore.createPlayer(playername.value);
}
</script>
