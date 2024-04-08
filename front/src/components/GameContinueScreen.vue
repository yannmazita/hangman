<template>
    <button class="btn" onclick="my_modal_5.showModal()">open modal</button>
    <dialog id="my_modal_5" class="modal modal-bottom">
        <div class="modal-box">
            <h3 class="font-bold text-lg">Hello!</h3>
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
</script
