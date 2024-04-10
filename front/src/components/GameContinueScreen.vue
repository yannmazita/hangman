<template>
    <dialog class="modal modal-bottom" :class="{ 'modal-open': showModal }">
        <div class="modal-box">
            <h3 class="font-bold text-lg">{{ message }}!</h3>
            <p class="py-4">Continue ?</p>
            <div class="modal-action">
                <form method="dialog">
                    <button @click="continueChoice = true" class="btn">Yes</button>
                    <button @click="continueChoice = false" class="btn">No</button>
                </form>
            </div>
        </div>
    </dialog>
</template>
<script setup lang="ts">
import { watch, ref, Ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useGameStore } from '@/stores/game.ts';

const { game } = storeToRefs(useGameStore());
const showModal = ref<boolean>(false);
const continueChoice = ref<boolean>(false);
const message: Ref<string> = ref("");

watch(game, (newGame) => {
    if (newGame.game_status !== 0) {
        showModal.value = true;
        if (newGame.game_status === 1) {
            message.value = "You won!"
        }
        else if (newGame.game_status === -1) {
            message.value = "You lost!"
        }
    }
});
</script>
