<template>
    <AppModal
        @click-event-a="() => {continueGame(true);}"
        @click-event-b="() => {continueGame(false);}"
        :show-modal="showModal">
        <template #headerText>{{ message }}</template>
        <template #paragraphText>Continue ?</template>
        <template #buttonTextA>Yes</template>
        <template #buttonTextB>Yes</template>
    </AppModal>
</template>
<script setup lang="ts">
import { computed, watch, ref, Ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useGameStore } from '@/stores/game.ts';
import { useUserStore } from '@/stores/user.ts';
import { useMenuStore } from '@/stores/menu.ts';
import AppModal from '@/components/AppModalTwoButtons.vue';

const userStore = useUserStore();
const menuStore = useMenuStore();
const gameStore = useGameStore();
const { game } = storeToRefs(useGameStore());
const showModal = ref<boolean>(false);
const message: Ref<string> = ref("");

const gameStatus = computed(() => {
    return game.value.game_status;
});

const continueGame = async function (choice: boolean) {
    if (choice) {
        showModal.value = false;
        try {
            await userStore.sendSocketMessage(JSON.stringify({
                action: 'continue_game',
                data: null
            }));
        } catch (error) {
            console.log(error);
        }
    }
    else {
        showModal.value = false;
        try {
            await userStore.sendSocketMessage(JSON.stringify({
                action: 'end_game',
                data: null
            }));
        } catch (error) {
            console.log(error);
        }

        gameStore.endGame();
        menuStore.resetChoices();
    }
};

watch(gameStatus, (newGameStatus) => {
    if (newGameStatus !== 0) {
        showModal.value = true;
        if (newGameStatus === 1) {
            message.value = "You won!"
        }
        else if (newGameStatus === -1) {
            message.value = "You lost!"
        }
    }
});
</script>
