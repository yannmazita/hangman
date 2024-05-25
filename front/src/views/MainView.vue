<template>
    <!--<div class="flex flex-col justify-between h-full max-w-full lg:grid lg:grid-cols-12">-->
    <div class="flex flex-col justify-between h-full max-w-full">
        <ProfileInformation v-if="visibleComponent == SelectScreen" />
        <KeepAlive include="GameView">
            <component :is="visibleComponent" />
        </KeepAlive>
        <MiscInformation v-if="visibleComponent == SelectScreen" />
    </div>
</template>
<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useMenuStore } from '@/stores/menu.ts';
import { PageType } from '@/enums.ts';
import SelectScreen from '@/views/SelectScreenView.vue';
import GameView from '@/views/GameView.vue';
import ProfileInformation from '@/components/GameProfileInformation.vue';
import MiscInformation from '@/components/GameMiscInformation.vue';

const menuStore = useMenuStore();

const visibleComponent = computed(() => {
    if (menuStore.currentPage === PageType.GAME) {
        return GameView;
    }
    else if (menuStore.currentPage === PageType.SELECT_SCREEN) {
        return SelectScreen;
    }
    else {
        return SelectScreen;
    }

});

onMounted(() => {
    menuStore.setCurrentPage(PageType.HOME);
});

</script>
