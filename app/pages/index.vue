<script setup lang="ts">
const recipeStore = useRecipeStore()
const router = useRouter()
const toast = useToast()
const route = useRoute()

// confirm.vue の「新しいレシピを生成する」ボタン経由で bypass=1 が付く
const bypassCache = computed(() => route.query.bypass === '1')

const selectedGenre = ref('一般的な料理')
const numDishes = ref(2)
const uploadedFiles = ref<File[]>([])
const imagePreviews = ref<string[]>([])
const ingredientsText = ref('')
const isIdentifying = ref(false)
const isGenerating = ref(false)
const isChoi = ref(false)
const useAll = ref(false)
const easyCooking = ref(false)
const extraRequest = ref('')
const fileInputRef = ref<HTMLInputElement>()

const genres = [
  '一般的な料理',
  '離乳食(5-6ヶ月)',
  '離乳食(7-8ヶ月)',
  '離乳食(9-11ヶ月)',
  '離乳食(12-18ヶ月)',
]

const handleFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (!input.files) return
  uploadedFiles.value = Array.from(input.files)
  generatePreviews()
}

const generatePreviews = () => {
  imagePreviews.value = []
  for (const file of uploadedFiles.value) {
    const reader = new FileReader()
    reader.onload = (e) => {
      if (e.target?.result) {
        imagePreviews.value.push(e.target.result as string)
      }
    }
    reader.readAsDataURL(file)
  }
}

const removeImage = (index: number) => {
  uploadedFiles.value.splice(index, 1)
  imagePreviews.value.splice(index, 1)
}

const resizeImageToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (event) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        let width = img.width
        let height = img.height
        const maxSize = 1024

        if (Math.max(width, height) > maxSize) {
          const ratio = maxSize / Math.max(width, height)
          width = Math.round(width * ratio)
          height = Math.round(height * ratio)
        }

        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')!
        ctx.drawImage(img, 0, 0, width, height)
        const dataUrl = canvas.toDataURL('image/jpeg', 0.85)
        resolve(dataUrl.split(',')[1])
      }
      img.src = event.target?.result as string
    }
    reader.readAsDataURL(file)
  })
}

const identifyIngredients = async () => {
  if (uploadedFiles.value.length === 0) return
  isIdentifying.value = true
  const existingText = ingredientsText.value.trim()
  let identifiedText = ''

  try {
    const base64Images: string[] = []
    for (const file of uploadedFiles.value) {
      base64Images.push(await resizeImageToBase64(file))
    }

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

    if (!response.ok) throw new Error('API error')

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
    await router.push('/confirm')
  } catch {
    toast.add({ title: 'エラー', description: 'レシピの生成に失敗しました', color: 'error' })
  } finally {
    isGenerating.value = false
  }
}
</script>

<template>
  <UContainer class="py-6 space-y-6">
    <!-- ページヘッダー -->
    <div class="space-y-1">
      <h1 class="text-2xl font-bold flex items-center gap-2">
        <UIcon name="i-ph-fire" class="w-6 h-6 text-amber-500" />
        レシピをつくる
      </h1>
      <p class="text-sm text-muted">食材を入力して献立をご提案します</p>
    </div>

    <!-- 設定カード -->
    <UCard class="shadow-lg shadow-amber-100/60 ring-1 ring-amber-100">
      <template #header>
        <div class="flex items-center gap-2">
          <UIcon name="i-ph-sliders-horizontal" class="w-5 h-5 text-amber-500" />
          <h2 class="font-bold">設定</h2>
        </div>
      </template>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1">ジャンル</label>
          <USelect v-model="selectedGenre" :items="genres" />
        </div>
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-2">品数</label>
          <div class="flex p-1 bg-gray-100 rounded-xl">
            <button
              v-for="n in [1, 2, 3]"
              :key="n"
              class="flex-1 py-2 text-sm font-bold transition-all rounded-lg"
              :class="numDishes === n
                ? 'bg-white text-amber-500 shadow-sm'
                : 'text-slate-400 hover:text-slate-600'"
              @click="numDishes = n"
            >
              {{ n }}品
            </button>
          </div>
        </div>
      </div>
    </UCard>

    <!-- 食材リスト -->
    <UCard class="shadow-lg shadow-amber-100/60 ring-1 ring-amber-100">
      <template #header>
        <div class="flex items-center gap-2">
          <UIcon name="i-ph-list-checks" class="w-5 h-5 text-amber-500" />
          <h2 class="font-bold">食材リスト</h2>
          <UBadge size="xs" variant="soft" color="primary">編集可</UBadge>
        </div>
      </template>

      <UTextarea
        v-model="ingredientsText"
        :rows="5"
        placeholder="例:&#10;鶏もも肉 300g&#10;玉ねぎ 1個&#10;にんじん 1本&#10;じゃがいも 2個"
      />

      <!-- 写真から読み取り（入力補助） -->
      <div class="mt-4 p-3 rounded-2xl bg-gray-50 border border-gray-200 space-y-3">
        <div class="text-xs font-bold uppercase tracking-wider text-gray-500 flex items-center gap-1">
          <UIcon name="i-ph-camera" class="w-3 h-3" />
          写真から読み取り
        </div>

        <div
          class="border-2 border-dashed border-amber-200 rounded-xl p-4 text-center cursor-pointer hover:border-amber-400 hover:bg-amber-50/50 transition-all"
          @click="fileInputRef?.click()"
        >
          <UIcon name="i-ph-image-square" class="w-8 h-8 text-amber-300 mx-auto mb-1" />
          <p class="text-xs font-medium text-slate-500">タップして写真を選択（複数可）</p>
          <input
            ref="fileInputRef"
            type="file"
            multiple
            accept="image/*"
            class="hidden"
            @change="handleFileChange"
          />
        </div>

        <!-- プレビュー -->
        <div v-if="imagePreviews.length" class="grid grid-cols-4 gap-2">
          <div v-for="(src, i) in imagePreviews" :key="i" class="relative animate-pop-in">
            <img :src="src" class="w-full h-20 object-cover rounded-xl border border-amber-100" />
            <button
              type="button"
              class="absolute -top-1.5 -right-1.5 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs shadow-sm"
              @click="removeImage(i)"
            >
              ×
            </button>
          </div>
        </div>

        <!-- 食材読み取りボタン -->
        <UButton
          v-if="uploadedFiles.length > 0"
          :loading="isIdentifying"
          color="neutral"
          variant="soft"
          size="sm"
          block
          icon="i-ph-magnifying-glass"
          class="font-bold"
          @click="identifyIngredients"
        >
          写真から食材を読み取る
        </UButton>
      </div>

      <div class="mt-4 space-y-3">
        <div class="p-3 rounded-2xl bg-amber-50 border border-amber-200 space-y-2">
          <div class="text-xs font-bold uppercase tracking-wider text-amber-600 flex items-center gap-1">
            <UIcon name="i-ph-sparkle" class="w-3 h-3" />
            オプション
          </div>
          <UCheckbox v-model="isChoi" label="ちょい足しモード（+2〜3品）" />
          <UCheckbox v-model="useAll" label="全食材を使うモード" />
          <UCheckbox v-model="easyCooking" label="お手軽調理（15分以内）" />
        </div>

        <UAccordion
          :items="[{ label: '追加の要望（任意）', content: '' }]"
        >
          <template #body>
            <UTextarea
              v-model="extraRequest"
              :rows="3"
              placeholder="例: 辛いものは避けて、和食でまとめてください..."
            />
          </template>
        </UAccordion>
      </div>
    </UCard>

    <!-- レシピ生成ボタン -->
    <UButton
      :loading="isGenerating"
      :disabled="!ingredientsText.trim()"
      color="primary"
      size="lg"
      block
      icon="i-ph-sparkle"
      class="font-extrabold text-base shadow-md shadow-amber-200 active-press"
      @click="generateRecipe"
    >
      レシピを生成する
    </UButton>
  </UContainer>
</template>
