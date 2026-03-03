<script setup lang="ts">
const recipeStore = useRecipeStore()
const toast = useToast()
const { isGenerationComplete } = useGeneratingOverlay()

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
    const end = i + 1 < matches.length ? (matches[i + 1]!.index ?? recipeText.value.length) : recipeText.value.length
    const fullSection = recipeText.value.slice(start, end)

    const nutritionMatch = fullSection.match(/###\s*栄養素概算[\s\S]*$/)
    const body = nutritionMatch
      ? fullSection.slice(0, nutritionMatch.index ?? fullSection.length).trim()
      : fullSection.trim()
    const nutrition = nutritionMatch ? nutritionMatch[0] : ''
    const bodyWithoutTitle = body.replace(/^##[^\n]*\n?/, '').trim()

    // ### 見出しから料理名を抽出（栄養素概算は除外）
    const dishNames = [...bodyWithoutTitle.matchAll(/^###\s+(.+)$/gm)]
      .map(m => (m[1] ?? '').trim())
      .filter(name => !name.includes('栄養素'))
    // 料理名が取れなければ ## 案X: の後ろをフォールバック
    const fallbackTitle = (fullSection.split('\n')[0] ?? '').replace(/#/g, '').replace(/^案[A-CＡ-Ｃ][:：]\s*/, '').trim()
    const title = dishNames.length > 0 ? dishNames.join('・') : fallbackTitle

    return { label: title, content: bodyWithoutTitle, nutrition }
  })
})

const activeTab = ref(0)

// 各案ごとの保存済みフラグ
const savedTabs = ref<Set<number>>(new Set())

const saveCurrentSection = () => {
  const section = recipeSections.value[activeTab.value]
  if (!section) return
  recipeStore.saveRecipe(section.label, section.content, section.nutrition || undefined)
  savedTabs.value = new Set([...savedTabs.value, activeTab.value])
  toast.add({ title: '保存しました', icon: 'i-ph-check-circle', color: 'success' })
}

const isSaved = computed(() => savedTabs.value.has(activeTab.value))

onMounted(() => {
  window.scrollTo({ top: 0, behavior: 'instant' })
  isGenerationComplete.value = false
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
          class="flex-1 py-2 text-sm font-bold transition-all rounded-lg relative"
          :class="activeTab === i
            ? 'bg-white text-amber-500 shadow-sm'
            : 'text-slate-400 hover:text-slate-600'"
          @click="activeTab = i"
        >
          {{ section.label.length > 12 ? section.label.slice(0, 12) + '…' : section.label }}
          <!-- 保存済みインジケーター -->
          <span
            v-if="savedTabs.has(i)"
            class="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-emerald-400"
          />
        </button>
      </div>

      <!-- レシピカード -->
      <RecipeCard
        v-for="(section, i) in recipeSections"
        v-show="recipeSections.length <= 1 || activeTab === i"
        :key="i"
        :title="section.label"
        :content="section.content"
        :nutrition="section.nutrition"
      />

      <!-- 保存ボタン -->
      <UButton
        :color="isSaved ? 'success' : 'primary'"
        size="lg"
        block
        :icon="isSaved ? 'i-ph-check-circle' : 'i-ph-bookmark-simple'"
        class="font-extrabold text-base shadow-md active-press transition-all duration-300"
        :class="isSaved ? 'shadow-green-200' : 'shadow-amber-200'"
        :disabled="isSaved"
        @click="saveCurrentSection"
      >
        {{ isSaved ? '保存済み' : 'このレシピを保存する' }}
      </UButton>
    </template>
  </UContainer>
</template>
