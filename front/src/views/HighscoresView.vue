<template></template>
<script setup lang="ts">
import { onMounted } from 'vue';
import { useMenuStore } from '@/stores/menu.ts';
import { PageType } from '@/enums.ts';

const menuStore = useMenuStore();
onMounted(() => {
    menuStore.setCurrentPage(PageType.HIGHSCORES);
});
</script>
