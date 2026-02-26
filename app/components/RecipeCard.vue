<script setup lang="ts">
const props = defineProps<{
  title: string
  content: string
  nutrition?: string
}>()

const { renderMarkdown } = useMarkdown()
</script>

<template>
  <div class="animate-pop-in">
    <UCard class="shadow-lg shadow-amber-100/60 ring-1 ring-amber-100">
      <template #header>
        <div class="flex items-center gap-2">
          <UIcon name="i-ph-bowl-food" class="w-5 h-5 text-amber-500" />
          <h2 class="font-bold text-sm">{{ title }}</h2>
        </div>
      </template>

      <div class="prose prose-sm prose-slate max-w-none" v-html="renderMarkdown(content)" />
    </UCard>

    <!-- 栄養素概算 -->
    <UCard
      v-if="nutrition"
      class="mt-3 shadow-sm ring-1 ring-emerald-100"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <UIcon name="i-ph-chart-bar" class="w-4 h-4 text-emerald-500" />
          <h3 class="font-bold text-xs text-emerald-700">栄養素概算</h3>
        </div>
      </template>
      <div class="prose prose-sm prose-slate max-w-none" v-html="renderMarkdown(nutrition)" />
    </UCard>
  </div>
</template>
