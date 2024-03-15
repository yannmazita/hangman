<template>
    <div class="flex flex-col">
        <h3 class="flex justify-center text-2xl">
            <slot name="formTitle"></slot>
        </h3>
        <form @submit="onSubmit" method="post">
            <div class="flex flex-col px-5">
                <AppInput v-model="username" :label="'Username'" type="text" />
            </div>
            <div class="flex flex-col px-5">
                <AppInput v-model="password" :label="'Password'" type="password" />
            </div>
            <div v-if="props.confirmPassword" class="flex flex-col px-5">
                <--! password confirmation input -->
            </div>
            <div class="flex justify-center">
                <AppButton :disabled="isSubmitting" type="submit">{{ 'Login' }}</AppButton>
            </div>
            <div class="flex justify-center">
                <div class="grid grid-flow-row">
                    <AppButton :disabled="isSubmitting" @click="goToSelectScreen">{{ 'Select Screen' }}</AppButton>
                </div>
            </div>
        </form>
    </div>
</template>
<script setup lang="ts">
import { useAuthenticationStore } from '@/stores/authentication.js';
import { useMenuStore } from '@/stores/menu.ts';
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/yup';
import { object, string } from 'yup';
import AppInput from '@/components/AppInput.vue';
import AppButton from '@/components/AppButton.vue';

const authenticationStore = useAuthenticationStore();
const menuStore = useMenuStore();

interface Props {
    confirmPassword?: boolean;
}
const props = defineProps<Props>();

const schema = toTypedSchema(
    object({
        username: string().required().min(3).max(20).default(''),
        password: string().required().min(1).max(20).default(''),
        //passwordConfirmation: string().required().min(8).max(20)
    }),
);
const { errors, handleSubmit, isSubmitting, defineField } = useForm({
    validationSchema: schema,
});

const [username] = defineField('username');
const [password] = defineField('password');
//const [passwordConfirmation, passwordConfirmationAttrs] = defineField('passwordConfirmation');

const onSubmit = handleSubmit(async (values, { resetForm }) => {
    const data = new FormData();
    data.append('username', values.username);
    data.append('password', values.password);
    data.append('scope',
        'user.create user:own user:own.write user:own:player user:own:player.write user:others:player:points user:others:player:playername websockets');
    const response = await authenticationStore.loginUser(data);
    await authenticationStore.getOwnUser();
    resetForm();
    return response;
});

const goToSelectScreen = function () {
    menuStore.resetChoices();
};

</script>
