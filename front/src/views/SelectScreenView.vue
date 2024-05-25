<template>
    <div class="flex flex-col">
        <h1 class="flex justify-center text-7xl pb-8">hangman</h1>
        <component class="" :is="visibleComponent" v-bind="currentProps">{{ currentSlot }}</component>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useMenuStore } from '@/stores/menu.ts';
import { useAuthenticationStore } from '@/stores/authentication.js'
import SelectMenu from '@/components/GameSelectMenu.vue';
import AuthForm from '@/components/GameAuthenticationForm.vue';
import { PageType } from '@/enums';

const menuStore = useMenuStore();
const authStore = useAuthenticationStore();
const currentSlot = ref('');
const currentProps = ref({});

const visibleComponent = computed(() => {
    if (menuStore.currentPage === PageType.AUTH && authStore.authenticated == false) {
        // User chose to log on and isn't authenticated.
        currentProps.value = { confirmPassword: false };
        return AuthForm;
    }
    else if (menuStore.currentPage === PageType.AUTH && authStore.authenticated != false) {
        // User chose to logon is authenticated. Send them back.
        //menuStore.resetPage();
        return SelectMenu;
    }
    else {
        return SelectMenu;
    }
})

onMounted(() => {
    menuStore.setCurrentPage(PageType.SELECT_SCREEN);
});

</script>
