<template>
    <button class="btn btn-ghost rounded-none text-3xl active:bg-transparent w-fit" @click="handleClick">
        <slot></slot>
    </button>
</template>
<script setup lang="ts">
const emit = defineEmits(['click']);

function handleClick() {
    emit('click')
}
</script>
