<script setup lang="ts">
const recipeStore = useRecipeStore()
const toast = useToast()
const { renderMarkdown } = useMarkdown()

const expandedIndex = ref<number | null>(null)
const deleteTargetIndex = ref<number | null>(null)

// タイトル編集
const editingIndex = ref<number | null>(null)
const editingTitle = ref('')
const editInputRef = ref<HTMLInputElement | null>(null)

const toggleExpand = (index: number) => {
  if (editingIndex.value !== null) return
  expandedIndex.value = expandedIndex.value === index ? null : index
}

const displayTitle = (title: string | undefined): string => {
  return (title ?? 'レシピ').replace(/^案[A-CＡ-Ｃ][:：]\s*/, '').trim() || 'レシピ'
}

const startEdit = (index: number, title: string | undefined, e: Event) => {
  e.stopPropagation()
  editingIndex.value = index
  editingTitle.value = displayTitle(title)
  nextTick(() => editInputRef.value?.focus())
}

const commitEdit = (index: number) => {
  const trimmed = editingTitle.value.trim()
  if (trimmed && trimmed !== displayTitle(recipeStore.savedRecipes[index]?.title)) {
    recipeStore.updateRecipeTitle(index, trimmed)
  }
  editingIndex.value = null
}

const cancelEdit = () => {
  editingIndex.value = null
}

// マークダウン記号を取り除いてプレビュー用テキストを生成
const stripMarkdown = (text: string): string => {
  return text
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/^\s*[-*+]\s+/gm, '')
    .replace(/^\s*\d+\.\s+/gm, '')
    .replace(/\n+/g, ' ')
    .trim()
}

const openDeleteConfirm = (index: number) => {
  deleteTargetIndex.value = index
}

const confirmDelete = () => {
  if (deleteTargetIndex.value === null) return
  if (expandedIndex.value === deleteTargetIndex.value) expandedIndex.value = null
  recipeStore.deleteRecipe(deleteTargetIndex.value)
  deleteTargetIndex.value = null
  toast.add({ title: '削除しました', icon: 'i-ph-trash', color: 'error' })
}
</script>

<template>
  <UContainer class="py-6 space-y-6">
    <!-- ページヘッダー -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold flex items-center gap-2">
        <UIcon name="i-ph-bookmark-simple" class="w-6 h-6 text-amber-500" />
        保存済みレシピ
      </h1>
      <UBadge v-if="recipeStore.savedRecipes.length > 0" variant="soft" color="primary" size="sm">
        {{ recipeStore.savedRecipes.length }}件
      </UBadge>
    </div>

    <!-- 空状態 -->
    <UCard v-if="recipeStore.savedRecipes.length === 0" class="shadow-lg shadow-amber-100/60 ring-1 ring-amber-100">
      <div class="text-center py-14">
        <UIcon name="i-ph-bookmark-simple" class="w-16 h-16 text-amber-200 mx-auto mb-4" />
        <p class="text-slate-500 font-medium">保存されたレシピはありません</p>
        <p class="text-sm text-slate-400 mt-1 mb-6">レシピを生成して保存してみましょう</p>
        <UButton to="/" color="primary" variant="soft" icon="i-ph-arrow-left">
          食材を解析する
        </UButton>
      </div>
    </UCard>

    <!-- レシピリスト -->
    <div v-else class="space-y-3">
      <UCard
        v-for="(recipe, i) in recipeStore.savedRecipes"
        :key="i"
        class="shadow-lg shadow-amber-100/60 ring-1 ring-amber-100 cursor-pointer transition-all duration-200 hover:ring-amber-300 hover:shadow-amber-200/80"
        @click="toggleExpand(i)"
      >
        <template #header>
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-start gap-2.5 min-w-0 flex-1">
              <div class="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                <UIcon name="i-ph-bowl-food" class="w-4 h-4 text-amber-500" />
              </div>
              <div class="min-w-0 flex-1">
                <!-- 編集モード -->
                <div v-if="editingIndex === i" class="flex items-center gap-1.5" @click.stop>
                  <input
                    ref="editInputRef"
                    v-model="editingTitle"
                    class="flex-1 text-sm font-bold text-slate-800 bg-amber-50 border border-amber-300 rounded px-2 py-0.5 outline-none focus:ring-2 focus:ring-amber-300 min-w-0"
                    @keydown.enter="commitEdit(i)"
                    @keydown.esc="cancelEdit"
                    @blur="commitEdit(i)"
                  />
                  <button class="text-emerald-500 hover:text-emerald-700 flex-shrink-0" @click.stop="commitEdit(i)">
                    <UIcon name="i-ph-check" class="w-4 h-4" />
                  </button>
                  <button class="text-slate-400 hover:text-slate-600 flex-shrink-0" @click.stop="cancelEdit">
                    <UIcon name="i-ph-x" class="w-4 h-4" />
                  </button>
                </div>

                <!-- 表示モード -->
                <div v-else class="flex items-center gap-1.5">
                  <p class="font-bold text-sm text-slate-800 leading-snug">
                    {{ displayTitle(recipe.title) }}
                  </p>
                  <button
                    class="text-slate-300 hover:text-amber-500 active:text-amber-600 flex-shrink-0 tap-target flex items-center"
                    @click.stop="startEdit(i, recipe.title, $event)"
                  >
                    <UIcon name="i-ph-pencil-simple" class="w-3.5 h-3.5" />
                  </button>
                </div>

                <p class="text-xs text-slate-400 mt-0.5">{{ recipe.date }}</p>
              </div>
            </div>
            <UIcon
              :name="expandedIndex === i ? 'i-ph-caret-up' : 'i-ph-caret-down'"
              class="w-4 h-4 text-slate-400 flex-shrink-0 mt-1 transition-transform duration-200"
            />
          </div>
        </template>

        <!-- 展開時 -->
        <div v-if="expandedIndex === i" class="animate-pop-in" @click.stop>
          <!-- レシピ本文 -->
          <div
            class="prose prose-sm prose-slate max-w-none
              prose-headings:text-slate-700 prose-headings:font-bold
              prose-h3:text-sm prose-h3:uppercase prose-h3:tracking-wide prose-h3:text-amber-600 prose-h3:border-b prose-h3:border-amber-100 prose-h3:pb-1 prose-h3:mb-2
              prose-ul:my-2 prose-li:my-0.5 prose-ol:my-2
              prose-strong:text-slate-700"
            v-html="renderMarkdown(recipe.content)"
          />

          <!-- 栄養素概算 -->
          <div v-if="recipe.nutrition" class="mt-4 pt-4 border-t border-slate-100">
            <div class="flex items-center gap-1.5 mb-2">
              <UIcon name="i-ph-chart-bar" class="w-4 h-4 text-emerald-500" />
              <span class="text-xs font-bold text-emerald-700 uppercase tracking-wide">栄養素概算</span>
            </div>
            <div
              class="prose prose-sm max-w-none prose-strong:text-emerald-700 prose-ul:my-1 prose-li:my-0"
              v-html="renderMarkdown(recipe.nutrition)"
            />
          </div>

          <!-- 削除ボタン -->
          <div class="mt-4 pt-3 border-t border-slate-100">
            <UButton
              color="error"
              variant="soft"
              size="sm"
              icon="i-ph-trash"
              class="active-press"
              @click="openDeleteConfirm(i)"
            >
              削除
            </UButton>
          </div>
        </div>

        <!-- 折りたたみ時: プレビューテキスト -->
        <p v-else class="text-sm text-slate-400 line-clamp-2 leading-relaxed">
          {{ stripMarkdown(recipe.content).slice(0, 120) }}
        </p>
      </UCard>
    </div>

    <!-- 削除確認ダイアログ -->
    <UModal
      :open="deleteTargetIndex !== null"
      title="レシピを削除しますか？"
      @update:open="(v) => { if (!v) deleteTargetIndex = null }"
    >
      <template #body>
        <p class="text-sm text-slate-600">
          「{{ deleteTargetIndex !== null ? displayTitle(recipeStore.savedRecipes[deleteTargetIndex]?.title) : '' }}」を削除します。この操作は元に戻せません。
        </p>
      </template>
      <template #footer>
        <div class="flex gap-2 justify-end w-full">
          <UButton variant="ghost" color="neutral" @click="deleteTargetIndex = null">
            キャンセル
          </UButton>
          <UButton color="error" icon="i-ph-trash" @click="confirmDelete">
            削除する
          </UButton>
        </div>
      </template>
    </UModal>
  </UContainer>
</template>
