<script setup lang="ts">
const recipeStore = useRecipeStore()
const router = useRouter()
const toast = useToast()
const route = useRoute()
const { remaining, isLimitReached, consume } = useGenerationLimit()

// confirm.vue の「新しいレシピを生成する」ボタン経由で bypass=1 が付く
const bypassCache = computed(() => route.query.bypass === '1')

const { isGenerating, isGenerationComplete } = useGeneratingOverlay()
const { isRetrying, retryCountdown, retryAttempt, fetchStream, cancel } = useStreamWithRetry()

const ingredientsText = ref('')
const isIdentifying = ref(false)
const showConfirmDialog = ref(false)
const selectedGenre = ref('一般的な料理')
const numDishes = ref(2)
const isChoi = ref(false)
const useAll = ref(false)
const easyCooking = ref(false)
const extraRequest = ref('')

const identifyIngredients = async (base64Images: string[]) => {
  isIdentifying.value = true
  const existingText = ingredientsText.value.trim()
  let identifiedText = ''

  try {
    await fetchStream(
      '/api/identify',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ images: base64Images }),
      },
      {
        maxRetries: 2,
        baseDelayMs: 1000,
        onChunk: (chunk: string) => { identifiedText += chunk },
        onError: (_message: string) => {
          toast.add({ title: 'エラー', description: '食材の読み取りに失敗しました', color: 'error' })
        },
      },
    )

    if (identifiedText) {
      ingredientsText.value = existingText
        ? existingText + '\n' + identifiedText
        : identifiedText
      recipeStore.setIngredients(ingredientsText.value)
    }
  } catch {
    toast.add({ title: 'エラー', description: '食材の読み取りに失敗しました', color: 'error' })
  } finally {
    isIdentifying.value = false
  }
}

const generateRecipe = async () => {
  if (!ingredientsText.value) return

  // 回数制限チェック
  if (!consume()) {
    toast.add({ title: '本日の上限に達しました', description: `レシピ生成は1日${5}回までです。明日またお試しください。`, color: 'warning' })
    return
  }

  isGenerating.value = true
  let result = ''

  try {
    await fetchStream(
      '/api/generate-recipe',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ingredients: ingredientsText.value,
          mode: selectedGenre.value,
          numDishes: numDishes.value,
          isChoi: isChoi.value,
          useAll: useAll.value,
          extraRequest: extraRequest.value,
          easyCooking: easyCooking.value,
          bypassCache: bypassCache.value,
        }),
      },
      {
        maxRetries: 3,
        baseDelayMs: 1000,
        onChunk: (chunk: string) => { result += chunk },
        onRetry: (_attempt: number, _delayMs: number, _reason: string) => {
          // リトライ中は isRetrying/retryCountdown のリアクティブ値でバナーを表示
        },
        onError: (message: string) => {
          isGenerating.value = false
          isGenerationComplete.value = false
          toast.add({ title: 'エラー', description: message, color: 'error' })
        },
      },
    )

    if (!result) return

    recipeStore.setRecipeResult(result)
    recipeStore.setIngredients(ingredientsText.value)

    // 完了アニメーションを表示してから遷移
    isGenerating.value = false
    isGenerationComplete.value = true
    await new Promise(resolve => setTimeout(resolve, 1500))
    await router.push('/confirm')
  } catch (err) {
    isGenerating.value = false
    isGenerationComplete.value = false
    const isNetworkError = err instanceof TypeError
    if ((err as any)?.status === 429) {
      toast.add({
        title: 'リクエスト過多',
        description: 'リトライ上限に達しました。しばらく経ってから再試行してください',
        color: 'warning',
      })
    } else {
      toast.add({
        title: 'エラー',
        description: isNetworkError
          ? 'ネットワークエラーが発生しました。接続を確認してください'
          : 'レシピの生成に失敗しました。もう一度お試しください',
        color: 'error',
      })
    }
  }
}

onUnmounted(() => cancel())
</script>

<template>
  <UContainer class="py-6 space-y-6">
    <!-- ページヘッダー -->
    <div class="space-y-1">
      <h1 class="text-2xl font-bold flex items-center gap-2">
        <UIcon name="i-ph-fire" class="w-6 h-6 text-amber-500" />
        何を作ろう？
      </h1>
      <p class="text-sm text-muted">入力した食材からレシピをご提案します</p>
    </div>

    <!-- 設定 -->
    <RecipeOptions
      v-model:genre="selectedGenre"
      v-model:numDishes="numDishes"
      v-model:isChoi="isChoi"
      v-model:useAll="useAll"
      v-model:easyCooking="easyCooking"
      v-model:extraRequest="extraRequest"
    />

    <!-- 食材リスト -->
    <UCard class="shadow-lg shadow-amber-100/60 ring-1 ring-amber-100">
      <template #header>
        <div class="flex items-center gap-2">
          <UIcon name="i-ph-list-checks" class="w-5 h-5 text-amber-500" />
          <h2 class="font-bold">食材リスト</h2>
          <UBadge size="xs" variant="soft" color="primary">編集可</UBadge>
        </div>
      </template>

      <IngredientInput v-model="ingredientsText" />

      <!-- 写真から読み取り -->
      <div class="mt-4">
        <ImageUpload
          :is-identifying="isIdentifying"
          @identify="identifyIngredients"
        />
      </div>
    </UCard>

    <!-- 残り回数表示 -->
    <div class="flex items-center justify-between text-sm">
      <span v-if="isLimitReached" class="text-red-500 font-medium flex items-center gap-1">
        <UIcon name="i-ph-warning-circle" class="w-4 h-4" />
        本日の生成上限に達しました
      </span>
      <span v-else class="text-slate-400">
        本日の残り生成回数:
        <span :class="remaining <= 1 ? 'text-orange-500 font-bold' : 'text-amber-500 font-bold'">{{ remaining }}回</span>
      </span>
    </div>

    <!-- リトライ待機バナー -->
    <div
      v-if="isRetrying"
      class="flex items-center gap-3 rounded-xl bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-700"
    >
      <UIcon name="i-ph-arrow-clockwise" class="w-4 h-4 shrink-0 animate-spin" />
      <span>
        レート制限中 — <span class="font-bold">{{ retryCountdown }}秒</span>後に再試行します
        <span class="text-amber-500 ml-1">({{ retryAttempt }}回目)</span>
      </span>
    </div>

    <!-- レシピ生成ボタン -->
    <UButton
      :disabled="isGenerating || !ingredientsText.trim() || isLimitReached"
      color="primary"
      size="lg"
      block
      icon="i-ph-sparkle"
      class="font-extrabold text-base shadow-md shadow-amber-200 active-press"
      @click="showConfirmDialog = true"
    >
      {{ isLimitReached ? '本日の上限に達しました' : 'レシピを考えて！' }}
    </UButton>

    <!-- 生成確認ダイアログ -->
    <RecipeConfirmDialog
      :open="showConfirmDialog"
      :genre="selectedGenre"
      :num-dishes="numDishes"
      :is-choi="isChoi"
      :use-all="useAll"
      :easy-cooking="easyCooking"
      :extra-request="extraRequest"
      :ingredients-text="ingredientsText"
      @confirm="showConfirmDialog = false; generateRecipe()"
      @cancel="showConfirmDialog = false"
    />

  </UContainer>
</template>
