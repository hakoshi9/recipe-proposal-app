<script setup lang="ts">
const recipeStore = useRecipeStore()
const toast = useToast()
const { isGenerationComplete } = useGeneratingOverlay()

const recipeText = computed(() => recipeStore.recipeResult)

const ingredientsSummary = computed(() => {
  const raw = recipeStore.ingredientsList?.trim()
  if (!raw) return ''
  const items = raw.split('\n').map(s => s.trim()).filter(Boolean)
  if (items.length <= 4) return items.join('、')
  return items.slice(0, 4).join('、') + `… 他${items.length - 4}品`
})

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

    const nutritionMatch = fullSection.match(/###\s*栄養素概算[\s\S]*$/)
    const body = nutritionMatch
      ? fullSection.slice(0, nutritionMatch.index).trim()
      : fullSection.trim()
    const nutrition = nutritionMatch ? nutritionMatch[0] : ''
    const titleLine = fullSection.split('\n')[0].replace(/#/g, '').trim()

    return { label: titleLine, content: body, nutrition }
  })
})

const activeTab = ref(0)

const isSaved = ref(false)

const saveRecipe = () => {
  recipeStore.saveRecipe()
  isSaved.value = true
  toast.add({ title: '保存しました', icon: 'i-ph-check-circle', color: 'success' })
}

onMounted(() => {
  window.scrollTo({ top: 0, behavior: 'instant' })
  isGenerationComplete.value = false
})
</script>

<template>
  <UContainer class="py-6 space-y-5">
    <!-- ページヘッダー -->
    <div class="space-y-1">
      <h1 class="text-2xl font-bold flex items-center gap-2">
        <UIcon name="i-ph-clipboard-text" class="w-6 h-6 text-amber-500" />
        できたレシピ
      </h1>
      <!-- 使用食材サマリ -->
      <p v-if="ingredientsSummary" class="text-xs text-slate-400 flex items-center gap-1 pl-0.5">
        <UIcon name="i-ph-carrot" class="w-3.5 h-3.5 flex-shrink-0" />
        {{ ingredientsSummary }}
      </p>
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
      <div v-if="recipeSections.length > 1" class="flex gap-2">
        <button
          v-for="(section, i) in recipeSections"
          :key="i"
          class="flex-1 py-2 px-3 text-sm font-bold rounded-xl border-2 transition-all duration-200"
          :class="activeTab === i
            ? 'border-amber-400 bg-amber-400 text-white shadow-md shadow-amber-200'
            : 'border-amber-100 bg-white text-slate-400 hover:border-amber-200 hover:text-slate-600'"
          @click="activeTab = i"
        >
          {{ section.label.length > 12 ? section.label.slice(0, 12) + '…' : section.label }}
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
      <div class="pt-1">
        <UButton
          :color="isSaved ? 'success' : 'primary'"
          size="lg"
          block
          :icon="isSaved ? 'i-ph-check-circle' : 'i-ph-bookmark-simple'"
          class="font-extrabold text-base shadow-md active-press transition-all duration-300"
          :class="isSaved ? 'shadow-green-200' : 'shadow-amber-200'"
          @click="saveRecipe"
        >
          {{ isSaved ? '保存済み' : 'このレシピを保存する' }}
        </UButton>
      </div>
    </template>
  </UContainer>
</template>
