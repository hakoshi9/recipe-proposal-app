<script setup lang="ts">
const model = defineModel<string>({ required: true })
</script>

<template>
  <UTextarea
    v-model="model"
    :rows="5"
    placeholder="例:&#10;鶏もも肉 300g&#10;玉ねぎ 1個&#10;にんじん 1本&#10;じゃがいも 2個"
  />
</template>
