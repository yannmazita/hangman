<template>
    <label v-if="label" class="label-text">{{ label }}</label>
    <input :value="modelValue" @input="updateModelValue" v-bind="{ ...$attrs, ...classes }" />
</template>
<script setup lang="ts">
import { computed } from 'vue';

interface Props {
    label?: string | boolean;
    class?: string | boolean;
    modelValue: string;
}

const props = defineProps<Props>();
const emit = defineEmits<{
    'update:modelValue': [value: string]
}>();

const classes = computed(() => {
    if (props.class) {
        return { class: props.class };
    }
    else {
        return { class: 'input input-bordered text-xl' };
    }
})

const updateModelValue = (e: Event) => {
    emit('update:modelValue', (e.target as HTMLInputElement).value);
}
</script>
