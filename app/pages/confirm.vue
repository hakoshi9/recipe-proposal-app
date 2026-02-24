<script setup lang="ts">
const recipeStore = useRecipeStore()
const toast = useToast()
const { renderMarkdown } = useMarkdown()

const recipeText = computed(() => recipeStore.recipeResult)

const recipeSections = computed(() => {
  if (!recipeText.value) return []

  const pattern = /##\s*案([A-CＡ-Ｃ])[:：]/g
  const matches = [...recipeText.value.matchAll(pattern)]

  if (matches.length === 0) {
    return [{ label: 'レシピ', content: recipeText.value, nutrition: '' }]
  }

  return matches.map((match, i) => {
    const start = match.index!
    const end = i + 1 < matches.length ? matches[i + 1].index! : recipeText.value.length
    const fullSection = recipeText.value.slice(start, end)
    const titleLine = fullSection.split('\n')[0].replace(/#/g, '').trim()

    const nutritionMatch = fullSection.match(/###\s*栄養素概算[\s\S]*$/)
    const body = nutritionMatch
      ? fullSection.slice(0, nutritionMatch.index).trim()
      : fullSection.trim()
    const nutrition = nutritionMatch ? nutritionMatch[0] : ''

    return { label: titleLine, content: body, nutrition }
  })
})

const activeTab = ref(0)

const saveRecipe = () => {
  recipeStore.saveRecipe()
  toast.add({ title: '保存しました', icon: 'i-ph-check-circle', color: 'success' })
}

onMounted(() => {
  window.scrollTo({ top: 0, behavior: 'instant' })
})
</script>

<template>
  <UContainer class="py-6 space-y-6">
    <!-- ページヘッダー -->
    <div class="space-y-1">
      <h1 class="text-2xl font-bold flex items-center gap-2">
        <UIcon name="i-ph-clipboard-text" class="w-6 h-6 text-amber-500" />
        できたレシピ
      </h1>
    </div>

    <!-- 空状態 -->
    <UCard v-if="!recipeText" class="shadow-lg shadow-amber-100/60 ring-1 ring-amber-100">
      <div class="text-center py-12">
        <UIcon name="i-ph-cooking-pot" class="w-16 h-16 text-amber-200 mx-auto mb-4" />
        <p class="text-slate-500 font-medium mb-4">まだレシピがありません</p>
        <UButton to="/" color="primary" variant="soft" icon="i-ph-arrow-left">
          食材を解析する
        </UButton>
      </div>
    </UCard>

    <template v-else>
      <!-- タブ切り替え -->
      <div v-if="recipeSections.length > 1" class="flex p-1 bg-gray-100 rounded-xl">
        <button
          v-for="(section, i) in recipeSections"
          :key="i"
          class="flex-1 py-2 text-sm font-bold transition-all rounded-lg"
          :class="activeTab === i
            ? 'bg-white text-amber-500 shadow-sm'
            : 'text-slate-400 hover:text-slate-600'"
          @click="activeTab = i"
        >
          {{ section.label.length > 12 ? section.label.slice(0, 12) + '…' : section.label }}
        </button>
      </div>

      <!-- レシピカード -->
      <div
        v-for="(section, i) in recipeSections"
        :key="i"
        v-show="recipeSections.length <= 1 || activeTab === i"
        class="animate-pop-in"
      >
        <UCard class="shadow-lg shadow-amber-100/60 ring-1 ring-amber-100">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-ph-bowl-food" class="w-5 h-5 text-amber-500" />
              <h2 class="font-bold text-sm">{{ section.label }}</h2>
            </div>
          </template>

          <div class="prose prose-sm prose-slate max-w-none" v-html="renderMarkdown(section.content)" />
        </UCard>

        <!-- 栄養素概算 -->
        <UCard
          v-if="section.nutrition"
          class="mt-3 shadow-sm ring-1 ring-emerald-100"
        >
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-ph-chart-bar" class="w-4 h-4 text-emerald-500" />
              <h3 class="font-bold text-xs text-emerald-700">栄養素概算</h3>
            </div>
          </template>
          <div class="prose prose-sm prose-slate max-w-none" v-html="renderMarkdown(section.nutrition)" />
        </UCard>
      </div>

      <!-- 保存ボタン -->
      <UButton
        color="primary"
        size="lg"
        block
        icon="i-ph-bookmark-simple"
        class="font-extrabold text-base shadow-md shadow-amber-200 active-press"
        @click="saveRecipe"
      >
        このレシピを保存する
      </UButton>

      <!-- 再生成ボタン -->
      <UButton
        to="/?bypass=1"
        color="neutral"
        variant="soft"
        size="lg"
        block
        icon="i-ph-arrow-counter-clockwise"
        class="font-bold text-base"
      >
        新しいレシピを生成する
      </UButton>
    </template>
  </UContainer>
</template>
