<script setup lang="ts">
const recipeStore = useRecipeStore()
const toast = useToast()
const { isGenerationComplete } = useGeneratingOverlay()
const { countdown, isWatchingFor, isUnlocked, watchAd, reset } = useRewardedAd()

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

const isLocked = (i: number) => i >= 1 && !isUnlocked(i)

const saveCurrentSection = () => {
  const section = recipeSections.value[activeTab.value]
  if (!section) return
  recipeStore.saveRecipe(section.label, section.content, section.nutrition || undefined)
  savedTabs.value = new Set([...savedTabs.value, activeTab.value])
  toast.add({ title: '保存しました', icon: 'i-ph-check-circle', color: 'success' })
}

const isSaved = computed(() => savedTabs.value.has(activeTab.value))

const handleWatchAd = async (index: number) => {
  await watchAd(index)
  toast.add({ title: '広告視聴完了！', description: `案${index + 1}が解放されました`, icon: 'i-ph-lock-open', color: 'success' })
}

onMounted(() => {
  window.scrollTo({ top: 0, behavior: 'instant' })
  isGenerationComplete.value = false
  reset()
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
          <span class="flex items-center justify-center gap-1">
            <UIcon v-if="isLocked(i)" name="i-ph-lock" class="w-3.5 h-3.5 text-slate-400" />
            {{ section.label.length > 12 ? section.label.slice(0, 12) + '…' : section.label }}
          </span>
          <!-- 保存済みインジケーター -->
          <span
            v-if="savedTabs.has(i)"
            class="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-emerald-400"
          />
        </button>
      </div>

      <!-- レシピカード（案1のみ） -->
      <RecipeCard
        v-show="recipeSections.length <= 1 || activeTab === 0"
        :title="recipeSections[0]?.label ?? ''"
        :content="recipeSections[0]?.content ?? ''"
        :nutrition="recipeSections[0]?.nutrition ?? ''"
      />

      <!-- 案2/3: ロック or 解放後表示 -->
      <template v-for="(section, i) in recipeSections" :key="i">
        <template v-if="i >= 1">
          <!-- ロック状態 -->
          <div
            v-if="isLocked(i) && activeTab === i"
            class="animate-pop-in"
          >
            <UCard class="shadow-lg shadow-amber-100/60 ring-1 ring-amber-100 overflow-hidden">
              <!-- タイトルはぼかしなしで表示 -->
              <template #header>
                <div class="flex items-center gap-2">
                  <UIcon name="i-ph-bowl-food" class="w-5 h-5 text-amber-500" />
                  <h2 class="font-bold text-sm">{{ section.label }}</h2>
                </div>
              </template>

              <!-- 広告解放ボタン（上寄せ） -->
              <div class="flex flex-col items-center gap-3 py-3">
                <UButton
                  color="primary"
                  icon="i-ph-play-circle"
                  size="md"
                  :loading="isWatchingFor(i)"
                  :disabled="isWatchingFor(i)"
                  @click="handleWatchAd(i)"
                >
                  {{ isWatchingFor(i) ? `広告を視聴中... (${countdown}秒)` : '広告を見て解放する' }}
                </UButton>
                <p class="text-slate-400 text-xs text-center">
                  <UIcon name="i-ph-lock" class="w-3 h-3 inline mr-0.5" />
                  案{{ i + 1 }}の内容は広告視聴後に表示されます
                </p>
              </div>

              <!-- 本文のみぼかし -->
              <div class="blur-sm pointer-events-none select-none opacity-40 -mx-4 -mb-4 px-4 pb-4 border-t border-amber-50 pt-3">
                <div class="prose prose-sm prose-slate max-w-none" v-html="'<p>' + section.content.slice(0, 200) + '…</p>'" />
              </div>
            </UCard>
          </div>

          <!-- 解放済み -->
          <RecipeCard
            v-if="!isLocked(i) && activeTab === i"
            :title="section.label"
            :content="section.content"
            :nutrition="section.nutrition"
          />
        </template>
      </template>

      <!-- 保存ボタン（ロック中は非表示） -->
      <UButton
        v-if="!isLocked(activeTab)"
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
