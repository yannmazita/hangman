import { defineStore } from 'pinia';
import { ref, Ref } from 'vue';

export const useMenuStore = defineStore('menu', () => {
    const playChoice: Ref<boolean> = ref(false); // The user has chosen to play.
    const loginChoice: Ref<boolean> = ref(false); // The user has chosen to login.
    const settingsChoice: Ref<boolean> = ref(false); // The user has chosen to go to settings.

    function setPlayChoice(value: boolean): void {
        playChoice.value = value;
        loginChoice.value = !value;
        settingsChoice.value = !value;
    }

    function setLoginChoice(value: boolean): void {
        playChoice.value = !value;
        loginChoice.value = value;
        settingsChoice.value = !value;
    }

    function setSettingsChoice(value: boolean): void {
        playChoice.value = !value;
        loginChoice.value = !value;
        settingsChoice.value = value;
    }

    function resetChoices(): void {
        playChoice.value = false;
        loginChoice.value = false;
        settingsChoice.value = false;
    }



    return {
        playChoice,
        loginChoice,
        settingsChoice,
        setPlayChoice,
        setLoginChoice,
        setSettingsChoice,
        resetChoices,
    }
})

