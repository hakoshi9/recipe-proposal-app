<script setup lang="ts">
const recipeStore = useRecipeStore()
const toast = useToast()
const { isGenerationComplete } = useGeneratingOverlay()

const recipeText = computed(() => recipeStore.recipeResult)

const ingredientsSummary = computed(() => {
  const raw = recipeStore.ingredientsList?.trim()
  if (!raw) return ''
  const items = raw.split('\n').map(s => s.trim()).filter(Boolean)
  return items.join('、')
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
    const bodyWithoutTitle = body.replace(/^##[^\n]*\n?/, '').trim()

    return { label: titleLine, content: bodyWithoutTitle, nutrition }
  })
})

const activeTab = ref(0)

const isSaved = ref(false)

const isDev = import.meta.dev

const loadDummyData = () => {
  recipeStore.setIngredients('鶏むね肉\nキャベツ\nにんじん\n玉ねぎ\nじゃがいも\nにんにく')
  recipeStore.setRecipeResult(`## 案A: 和食定食セット
調理時間: 約25分

### 鶏むね肉の照り焼き
**材料と分量:**
- 鶏むね肉: 300g
- 醤油: 大さじ2
- みりん: 大さじ2
- 砂糖: 大さじ1
- サラダ油: 少々

**手順:**
1. 鶏むね肉を一口大に切り、フォークで数か所刺す
2. 醤油・みりん・砂糖を合わせてタレを作る
3. フライパンに油を熱し、鶏肉を中火で両面こんがり焼く
4. タレを加えて絡めながら煮詰めて完成

**ポイント:** 蓋をして蒸し焼きにすると中まで火が通りやすい

### 玉ねぎとにんじんの味噌汁
**材料と分量:**
- 玉ねぎ: 1/2個
- にんじん: 1/3本
- 味噌: 大さじ1.5
- だし汁: 400ml

**手順:**
1. 玉ねぎ・にんじんを薄切りにする
2. だし汁で野菜をやわらかくなるまで煮る
3. 火を止めて味噌を溶かして完成

**ポイント:** 沸騰後は弱火でじっくり煮ると甘みが出る

### 栄養素概算
- カロリー: 約520kcal
- タンパク質: 35g
- 脂質: 8g
- 炭水化物: 72g

## 案B: 洋風ワンプレート
調理時間: 約20分

### 鶏野菜のソテー
**材料と分量:**
- 鶏むね肉: 200g
- キャベツ: 1/4個
- にんじん: 1本
- にんにく: 1片
- オリーブオイル: 大さじ1
- 塩コショウ: 適量

**手順:**
1. 鶏肉・野菜をひと口大に切る
2. にんにくを炒めて香りを出す
3. 鶏肉を加えて焼き色をつけてから野菜を炒める
4. 塩コショウで味を整えて完成

**ポイント:** 強火で手早く炒めると野菜の食感が残る

### キャベツのコールスロー
**材料と分量:**
- キャベツ: 1/8個
- マヨネーズ: 大さじ2
- 酢: 小さじ1
- 塩コショウ: 少々

**手順:**
1. キャベツを千切りにして塩もみする
2. 水気を絞り、マヨネーズ・酢・塩コショウで和える

**ポイント:** 食べる直前に和えると水っぽくならない

### 栄養素概算
- カロリー: 約420kcal
- タンパク質: 32g
- 脂質: 14g
- 炭水化物: 38g
`)
}

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
        <div class="flex flex-col items-center gap-3">
          <UButton to="/" color="primary" variant="soft" icon="i-ph-arrow-left">
            食材を解析する
          </UButton>
          <!-- 開発環境のみ表示 -->
          <UButton v-if="isDev" color="neutral" variant="outline" size="sm" icon="i-ph-flask" @click="loadDummyData">
            ダミーデータを読み込む
          </UButton>
        </div>
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
