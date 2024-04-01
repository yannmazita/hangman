import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useElementPropertiesStore = defineStore('elementProperties', () => {
    const navbarHeight = ref(0); // The height of the navbar.

    return {
        navbarHeight,
    }
})
