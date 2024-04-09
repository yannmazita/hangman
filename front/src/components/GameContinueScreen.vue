<template>
    <dialog ref="continueModal" class="modal modal-bottom">
        <div class="modal-box">
            <h3 class="font-bold text-lg">{{ message }}!</h3>
            <p class="py-4">Continue ?</p>
            <div class="modal-action">
                <form method="dialog">
                    <button class="btn">Yes</button>
                    <button class="btn">No</button>
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
const continueModal = ref<HTMLElement | null>(null);
const message: Ref<string> = ref("");

watch(game, (newGame) => {
    if (newGame.game_status !== 0) {
        continueModal.value?.showModal();
        if (newGame.game_status === 1) {
        }
        else if (newGame.game_status === -1) {
        }
    }
});
</script>
