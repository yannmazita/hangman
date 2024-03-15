<template>
    <form @submit="onSubmit" method="post">
        <div class="flex flex-col px-5">
            <AppInput v-model="character" placeholder="Type a letter" type="text" />
        </div>
        <div class="flex justify-center">
            <AppButton :disabled="isSubmitting" type="submit">{{ 'Confirm' }}</AppButton>
        </div>
    </form>
</template>
<script setup lang="ts">
import { useUserStore } from '@/stores/user.js';
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/yup';
import { object, string } from 'yup';
import AppInput from '@/components/AppInput.vue';
import AppButton from '@/components/AppButton.vue';

const userStore = useUserStore();

const schema = toTypedSchema(
    object({
        character: string().required().min(1).max(1).default(''),
    }),
);
const { errors, handleSubmit, isSubmitting, defineField } = useForm({
    validationSchema: schema,
});
const [character] = defineField('character');

const onSubmit = handleSubmit(async (values, { resetForm }) => {
    const message = JSON.stringify({
        action: 'guess_letter',
        data: {
            letter: values.character,
        },
    });
    userStore.sendSocketMessage(message);
    resetForm();
});
</script>
