<template>
    <div class="collapse collapse-arrow bg-base-100 rounded-none lg:col-start-10 lg:col-end-13">
        <input type="checkbox" />
        <div class="collapse-title text-xl">
            Server information (EU-West)
        </div>
        <div class="collapse-content bg-base-200">
            Online players: {{ activePlayers }}
        </div>
    </div>
</template>
<script setup lang="ts">
import { computed, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useGameStore } from '@/stores/game.ts';
import { useClientStore } from '@/stores/client.js';

const gameStore = useGameStore();
const clientStore = useClientStore();
const { serverStats } = storeToRefs(gameStore);
const { socketMessage } = storeToRefs(clientStore);

const activePlayers = computed(() => {
    return serverStats.value.active_players;
});

// move this to @/stores/games.ts
watch(socketMessage, (message) => {
    if (message.action === 'server_stats') {
        gameStore.serverStats.active_players = message.data.active_players;
    }
});
</script>
