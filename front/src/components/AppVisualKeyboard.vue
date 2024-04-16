<template>
    <div id="app-visual-keyboard-container" class="py-8">
        <div :id="`app-visual-keyboard-row-container-${index}`" v-for="(row, index) in keyboardRows" :key="index">
            <div :id="`app-visual-keyboard-row-${index}`" class="flex justify-center">
                <button :id="`app-visual-keyboard-key-${key}`" v-for="key in row" :key="key" @click="emit('keyPress', key)"
                    class="kbd text-white bg-cyan-700 m-1" type="submit">
                    {{ key }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
    keyboardKeys?: string[];
    hiddenKeys?: string[];
}

const props = withDefaults(defineProps<Props>(), {
    keyboardKeys: [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
    ],
    hiddenKeys: []
});
const emit = defineEmits<{
    keyPress: [key: string]
}>();

const keyboardRows = computed(() => {
    const visibleKeys = props.keyboardKeys.filter(key => !props.hiddenKeys.includes(key));
    const rows = [];
    for (let i = 0; i < Math.ceil(visibleKeys.length / 7); i++) {
        rows.push(visibleKeys.slice(i * 7, (i + 1) * 7));
    }
    return rows;
});
</script>
