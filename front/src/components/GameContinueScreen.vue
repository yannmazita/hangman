<template>
    <dialog class="modal modal-bottom" :class="{ 'modal-open': showModal }">
        <div class="modal-box">
            <h3 class="font-bold text-lg">{{ message }}</h3>
            <p class="py-4">Continue ?</p>
            <div class="modal-action">
                <form method="dialog">
                    <button @click="continueGame(true)" class="btn">Yes</button>
                    <button @click="continueGame(false)" class="btn">No</button>
                </form>
            </div>
        </div>
    </dialog>
</template>
<script setup lang="ts">
import { computed, watch, ref, Ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useGameStore } from '@/stores/game.ts';
import { useClientStore } from '@/stores/client.ts';
import { useMenuStore } from '@/stores/menu.ts';

const clientStore = useClientStore();
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
            await clientStore.sendSocketMessage(JSON.stringify({
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
            await clientStore.sendSocketMessage(JSON.stringify({
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
