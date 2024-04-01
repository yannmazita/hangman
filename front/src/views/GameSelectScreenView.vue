<template>
    <div class="flex flex-col">
        <h1 class="flex justify-center text-7xl pb-8">hangman</h1>
        <component class="" :is="visibleComponent" v-bind="currentProps">{{ currentSlot }}</component>
    </div>
</template>

<script setup lang="ts">
import { useMenuStore } from '@/stores/menu.ts';
import { useAuthenticationStore } from '@/stores/authentication.js'
import { ref, computed } from 'vue';
import SelectMenu from '@/components/GameSelectMenu.vue';
import AuthForm from '@/components/GameAuthenticationForm.vue';

const menuStore = useMenuStore();
const authStore = useAuthenticationStore();
const currentSlot = ref('');
const currentProps = ref({});

const visibleComponent = computed(() => {
    if (menuStore.loginChoice && authStore.authenticated == false) {
        // User chose to log on and isn't authenticated.
        currentProps.value = { confirmPassword: false };
        return AuthForm;
    }
    else if (menuStore.loginChoice && authStore.authenticated != false) {
        // User chose to logon is authenticated. Send them back.
        menuStore.resetChoices();
        return SelectMenu;
    }
    else {
        return SelectMenu;
    }
})

</script>
