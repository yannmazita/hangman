<template>
    <form @submit="onSubmit" method="post">
        <div class="bg-base-300">
            <Keyboard @keyPress="(key) => { updateAppInput(key); }" :hiddenKeys="[]"></Keyboard>
            <AppInput v-model="character" type="hidden"></AppInput>
        </div>
    </form>
</template>
<script setup lang="ts">
import { useUserStore } from '@/stores/user.js';
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/yup';
import { object, string } from 'yup';
import AppInput from '@/components/AppInput.vue';
import Keyboard from '@/components/AppVisualKeyboard.vue';

const userStore = useUserStore();

const schema = toTypedSchema(
    object({
        character: string().required().min(1).max(1).default(''),
    }),
);
const { handleSubmit, defineField } = useForm({
    validationSchema: schema,
});
const [character] = defineField('character');

const onSubmit = handleSubmit(async (values, { resetForm }) => {
    const message = JSON.stringify({
        action: 'guess_letter',
        data: {
            letter: values.character.toLowerCase(),
        },
    });
    userStore.sendSocketMessage(message);
    resetForm();
});

const updateAppInput = (key: string) => {
    character.value = key;
};

</script>
