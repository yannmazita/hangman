<template>
    <div id="game-character-input-container">
        <form @submit="onSubmit" method="post">
            <div class="bg-base-300">
                <Keyboard @keyPress="(key) => { updateAppInput(key); }" :hiddenKeys="[]"></Keyboard>
                <AppInput v-model="character" type="hidden"></AppInput>
            </div>
        </form>
    </div>
</template>
<script setup lang="ts">
import { useAppStore } from '@/stores/app.ts';
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/yup';
import { object, string } from 'yup';
import AppInput from '@/components/AppInput.vue';
import Keyboard from '@/components/AppVisualKeyboard.vue';

const appStore = useAppStore();

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
    await appStore.guessCharacter(values.character.toLowerCase());
    resetForm();
});

const updateAppInput = (key: string) => {
    character.value = key;
};

</script>
