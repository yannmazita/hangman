<template>
    <AppModal @click-event-a="() => { continueGame(true); }" @click-event-b="() => { continueGame(false); }"
        :show-modal="showModal">
        <template #headerText>{{ message }}</template>
        <template #paragraphText>Continue ?</template>
        <template #buttonTextA>Yes</template>
        <template #buttonTextB>No</template>
    </AppModal>
</template>
<script setup lang="ts">
import { computed, watch, ref, Ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useAppStore } from '@/stores/app.ts';
import { useMenuStore } from '@/stores/menu.ts';
import { PageType } from '@/enums.ts';
import AppModal from '@/components/AppModalTwoButtons.vue';

const menuStore = useMenuStore();
const appStore = useAppStore();
const { game } = storeToRefs(useAppStore());
const showModal: Ref<boolean> = ref(false);
const message: Ref<string> = ref("");

const gameStatus = computed(() => {
    return game.value.game_status;
});

const continueGame = async function (choice: boolean) {
    if (choice) {
        showModal.value = false;
        await appStore.continueGame();
    }
    else {
        showModal.value = false;
        await appStore.endGame();
        menuStore.setCurrentPage(PageType.SELECT_SCREEN);
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
