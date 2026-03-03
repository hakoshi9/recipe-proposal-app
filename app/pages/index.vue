<script setup lang="ts">
const recipeStore = useRecipeStore()
const router = useRouter()
const toast = useToast()
const route = useRoute()

// confirm.vue の「新しいレシピを生成する」ボタン経由で bypass=1 が付く
const bypassCache = computed(() => route.query.bypass === '1')

const { isGenerating, isGenerationComplete } = useGeneratingOverlay()

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
    const response = await fetch('/api/identify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ images: base64Images }),
    })

    if (!response.ok) throw new Error('API error')

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    if (!reader) throw new Error('No reader')

    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') break
          try {
            identifiedText += JSON.parse(data)
          } catch {
            identifiedText += data
          }
        }
      }
    }

    ingredientsText.value = existingText
      ? existingText + '\n' + identifiedText
      : identifiedText
    recipeStore.setIngredients(ingredientsText.value)
  } catch {
    toast.add({ title: 'エラー', description: '食材の読み取りに失敗しました', color: 'error' })
  } finally {
    isIdentifying.value = false
  }
}

const generateRecipe = async () => {
  if (!ingredientsText.value) return
  isGenerating.value = true

  try {
    const response = await fetch('/api/generate-recipe', {
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
    })

    if (!response.ok) {
      if (response.status === 429) {
        toast.add({ title: 'リクエスト過多', description: 'しばらく経ってから再試行してください（約1分後）', color: 'warning' })
      } else {
        toast.add({ title: 'エラー', description: `レシピの生成に失敗しました (${response.status})`, color: 'error' })
      }
      return
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    if (!reader) throw new Error('No reader')

    let result = ''
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') break
          try {
            result += JSON.parse(data)
          } catch {
            result += data
          }
        }
      }
    }

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
    const isNetworkError = err instanceof TypeError && err.message.includes('fetch')
    toast.add({
      title: 'エラー',
      description: isNetworkError
        ? 'ネットワークエラーが発生しました。接続を確認してください'
        : 'レシピの生成に失敗しました。もう一度お試しください',
      color: 'error',
    })
  }
}
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

    <!-- レシピ生成ボタン -->
    <UButton
      :disabled="isGenerating || !ingredientsText.trim()"
      color="primary"
      size="lg"
      block
      icon="i-ph-sparkle"
      class="font-extrabold text-base shadow-md shadow-amber-200 active-press"
      @click="showConfirmDialog = true"
    >
      レシピを考えて！
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
