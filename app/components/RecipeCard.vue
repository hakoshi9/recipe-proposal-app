<script setup lang="ts">
const props = defineProps<{
  title: string
  content: string
  nutrition?: string
}>()

const { renderMarkdown } = useMarkdown()

// ### 見出しが複数ある（= 複数品）場合のみ「N品目」ラベルを付ける
const processedContent = computed(() => {
  const headingMatches = [...props.content.matchAll(/^###\s+.+$/gm)]
  if (headingMatches.length <= 1) return props.content

  let index = 0
  return props.content.replace(/^(###\s+)(.+)$/gm, (_, hashes, name) => {
    index++
    return `${hashes}${index}品目：${name}`
  })
})
</script>

<template>
  <div class="animate-pop-in">
    <UCard class="shadow-lg shadow-amber-100/60 ring-1 ring-amber-100 overflow-hidden">
      <template #header>
        <div class="flex items-center gap-3 py-1">
          <div class="w-9 h-9 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
            <UIcon name="i-ph-bowl-food" class="w-5 h-5 text-amber-500" />
          </div>
          <h2 class="font-bold text-base leading-tight">{{ title }}</h2>
        </div>
      </template>

      <div
        class="prose prose-sm prose-slate max-w-none
          prose-headings:text-slate-700 prose-headings:font-bold
          prose-h3:text-sm prose-h3:uppercase prose-h3:tracking-wide prose-h3:text-amber-600 prose-h3:border-b prose-h3:border-amber-100 prose-h3:pb-1 prose-h3:mb-2
          prose-ul:my-2 prose-li:my-0.5
          prose-ol:my-2
          prose-strong:text-slate-700"
        v-html="renderMarkdown(processedContent)"
      />
    </UCard>

    <!-- 栄養素概算 -->
    <UCard
      v-if="nutrition"
      class="mt-3 shadow-sm ring-1 ring-emerald-100 bg-emerald-50/40"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
            <UIcon name="i-ph-chart-bar" class="w-4 h-4 text-emerald-500" />
          </div>
          <h3 class="font-bold text-sm text-emerald-700">栄養素概算</h3>
        </div>
      </template>
      <div
        class="prose prose-sm prose-slate max-w-none
          prose-strong:text-emerald-700
          prose-ul:my-1 prose-li:my-0"
        v-html="renderMarkdown(nutrition)"
      />
    </UCard>
  </div>
</template>
