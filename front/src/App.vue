<template>
    <div class="grid grid-cols-12">
        <div class="col-span-12"></div>
        <NavBar class="col-span-12"></NavBar>
        <main class="col-span-12 h-[calc(100vh-48px)] p-3.5 lg:p-6">
            <router-view></router-view>
        </main>
        <AppFooter class="col-span-12"></AppFooter>
    </div>
</template>

<script setup lang="ts">
import NavBar from '@/components/AppNavBar.vue'
import AppFooter from '@/components/AppFooter.vue'
import { onMounted } from 'vue';
import { useClientStore } from '@/stores/client.ts';

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
