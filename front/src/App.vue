<template>
    <NavBar />
    <main>
        <div class="flex flex-row flex-nowrap">
            <div class="w-full flex-none">
                <img v-bind="backgroundProperties">
            </div>
            <div class="w-full flex-none ml-[-100%]">
                <router-view></router-view>
            </div>
        </div>
    </main>
    <AppFooter />
</template>

<script setup lang="ts">
import NavBar from '@/components/AppNavBar.vue'
import AppFooter from '@/components/AppFooter.vue'
import background from '@/assets/background_black.jpg';
import { reactive, onMounted } from 'vue';
import { useClientStore } from '@/stores/client.ts';

const backgroundProperties = reactive({
    src: background,
    alt: 'Montreuil, Japan',
    class: `object-cover h-[calc(100vh-48px)] w-screen`,
});
const clientStore = useClientStore();

onMounted(async () => {
    try {
        await clientStore.connectSocket();
        await clientStore.sendSocketMessage(JSON.stringify({
            action: 'server_stats',
            data: null
        }));
    } catch (error) {
        console.log(error)
    }
});
</script>
