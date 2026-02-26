<script setup lang="ts">
const props = defineProps<{
  content: string
  loading?: boolean
}>()

const { renderMarkdown } = useMarkdown()
</script>

<template>
  <div>
    <!-- ローディング中のスケルトン -->
    <div v-if="loading && !content" class="space-y-3 animate-pulse">
      <div class="h-4 bg-amber-100 rounded w-3/4" />
      <div class="h-4 bg-amber-100 rounded w-full" />
      <div class="h-4 bg-amber-100 rounded w-5/6" />
      <div class="h-4 bg-amber-100 rounded w-full" />
      <div class="h-4 bg-amber-100 rounded w-2/3" />
    </div>

    <!-- コンテンツ表示 -->
    <div
      v-if="content"
      class="prose prose-sm prose-slate max-w-none"
      :class="loading ? 'opacity-80' : ''"
      v-html="renderMarkdown(content)"
    />
  </div>
</template>
