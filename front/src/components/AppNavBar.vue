<template>
    <!--<div ref="navBar" class="navbar bg-cyan-600 text-white min-h-min py-0 lg:py-2">-->
    <div ref="navBar" class="navbar bg-cyan-600 text-white min-h-min py-0">
        <div class="navbar-start">
            <details class="dropdown">
                <!--<summary class="btn btn-ghost lg:hidden">-->
                <summary class="btn btn-ghost">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" />
                    </svg>
                </summary>
                <ul class="menu menu-sm dropdown-content mt-3 z-50 p-2 shadow bg-cyan-700 rounded-box w-52">
                    <li><router-link to="/highscores" class="text-xl">high scores</router-link></li>
                    <li><router-link to="/feedback" class="text-xl">feedback</router-link></li>
                </ul>
            </details>
            <router-link to="/" class="btn btn-ghost text-2xl">hangman</router-link>
        </div>

        <!--<div class="navbar-center hidden lg:flex">-->
        <div class="navbar-center hidden">
            <ul class="menu menu-horizontal px-1">
                <li><router-link to="/highscores" class="text-2xl xl:text-base">high scores</router-link></li>
                <li><router-link to="/feedback" class="text-2xl xl:text-base">feedback</router-link></li>
            </ul>
        </div>
        <div class="navbar-end">
        </div>
    </div>
</template>


<script setup lang="ts">
import { ref, onMounted, onUpdated } from 'vue';

const navBar = ref(null);
const height = ref(0);
const emit = defineEmits(['onHeightChange']);

onMounted(() => {
    height.value = parseFloat(window.getComputedStyle(navBar.value).height);
    emit('onHeightChange', height.value);
});

onUpdated(() => {
    height.value = parseFloat(window.getComputedStyle(navBar.value).height);
    emit('onHeightChange', height.value);
});
</script>
