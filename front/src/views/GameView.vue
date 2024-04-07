<template>
    <!--<div class="flex flex-col justify-between h-full max-w-full lg:grid lg:grid-cols-12">-->
    <div class="flex flex-col justify-between h-full max-w-full">
        <ProfileInformation v-if="visibleComponent == SelectScreen" />
        <KeepAlive include="GameMainView">
            <component :is="visibleComponent" />
        </KeepAlive>
        <MiscInformation v-if="visibleComponent == SelectScreen" />
    </div>
</template>
<script setup lang="ts">
import { useMenuStore } from '@/stores/menu.ts';
import { computed } from 'vue';
import SelectScreen from '@/views/GameSelectScreenView.vue';
import MainView from '@/views/GameMainView.vue';
import ProfileInformation from '@/components/GameProfileInformation.vue';
import MiscInformation from '@/components/GameMiscInformation.vue';

const menuStore = useMenuStore();

const visibleComponent = computed(() => {
    if (menuStore.playChoice) {
        return MainView;
    }
    else if (menuStore.loginChoice) {
        return SelectScreen;
    }
    else {
        return SelectScreen;
    }

});

</script>
