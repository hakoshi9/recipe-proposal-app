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
    <div v-if="loading && !content" class="space-y-4">
      <!-- タイトル行 -->
      <div class="h-5 bg-amber-100 rounded-md w-2/3 skeleton-shimmer" />
      <!-- テキスト行群 -->
      <div class="space-y-2">
        <div class="h-3.5 bg-amber-100 rounded w-full skeleton-shimmer" />
        <div class="h-3.5 bg-amber-100 rounded w-5/6 skeleton-shimmer" />
        <div class="h-3.5 bg-amber-100 rounded w-full skeleton-shimmer" />
        <div class="h-3.5 bg-amber-100 rounded w-4/5 skeleton-shimmer" />
      </div>
      <!-- サブタイトル -->
      <div class="h-4 bg-amber-100 rounded-md w-1/2 skeleton-shimmer mt-2" />
      <!-- リスト項目 -->
      <div class="space-y-2 pl-2">
        <div class="h-3.5 bg-amber-100 rounded w-3/4 skeleton-shimmer" />
        <div class="h-3.5 bg-amber-100 rounded w-2/3 skeleton-shimmer" />
        <div class="h-3.5 bg-amber-100 rounded w-4/5 skeleton-shimmer" />
        <div class="h-3.5 bg-amber-100 rounded w-3/5 skeleton-shimmer" />
      </div>
      <!-- サブタイトル2 -->
      <div class="h-4 bg-amber-100 rounded-md w-2/5 skeleton-shimmer" />
      <!-- ステップ -->
      <div class="space-y-2 pl-2">
        <div class="h-3.5 bg-amber-100 rounded w-full skeleton-shimmer" />
        <div class="h-3.5 bg-amber-100 rounded w-5/6 skeleton-shimmer" />
        <div class="h-3.5 bg-amber-100 rounded w-full skeleton-shimmer" />
      </div>
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
