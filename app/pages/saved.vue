<script setup lang="ts">
const recipeStore = useRecipeStore()
const toast = useToast()
const { renderMarkdown } = useMarkdown()

const expandedIndex = ref<number | null>(null)

const toggleExpand = (index: number) => {
  expandedIndex.value = expandedIndex.value === index ? null : index
}

const deleteRecipe = (index: number) => {
  recipeStore.deleteRecipe(index)
  expandedIndex.value = null
  toast.add({ title: '削除しました', icon: 'i-ph-trash', color: 'success' })
}
</script>

<template>
  <UContainer class="py-6 space-y-6">
    <!-- ページヘッダー -->
    <div class="space-y-1">
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold flex items-center gap-2">
          <UIcon name="i-ph-bookmark-simple" class="w-6 h-6 text-amber-500" />
          保存済みレシピ
        </h1>
        <UBadge v-if="recipeStore.savedRecipes.length > 0" variant="soft" color="primary" size="sm">
          {{ recipeStore.savedRecipes.length }}件
        </UBadge>
      </div>
    </div>

    <!-- 空状態 -->
    <UCard v-if="recipeStore.savedRecipes.length === 0" class="shadow-lg shadow-amber-100/60 ring-1 ring-amber-100">
      <div class="text-center py-12">
        <UIcon name="i-ph-bookmark-simple" class="w-16 h-16 text-amber-200 mx-auto mb-4" />
        <p class="text-slate-500 font-medium">保存されたレシピはありません</p>
        <p class="text-sm text-slate-400 mt-1">レシピを生成して保存してみましょう</p>
      </div>
    </UCard>

    <!-- レシピリスト -->
    <div v-else class="space-y-3">
      <UCard
        v-for="(recipe, i) in recipeStore.savedRecipes"
        :key="i"
        class="shadow-lg shadow-amber-100/60 ring-1 ring-amber-100 cursor-pointer transition-all hover:ring-amber-300"
        @click="toggleExpand(i)"
      >
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-ph-bowl-food" class="w-5 h-5 text-amber-500" />
              <span class="font-bold text-sm">{{ recipe.date }} のレシピ</span>
            </div>
            <UIcon
              :name="expandedIndex === i ? 'i-ph-caret-up' : 'i-ph-caret-down'"
              class="w-4 h-4 text-slate-400 transition-transform"
            />
          </div>
        </template>

        <div
          v-if="expandedIndex === i"
          class="animate-pop-in"
        >
          <div class="prose prose-sm prose-slate max-w-none mb-4" v-html="renderMarkdown(recipe.content)" />
          <UButton
            color="error"
            variant="soft"
            size="sm"
            icon="i-ph-trash"
            @click.stop="deleteRecipe(i)"
          >
            削除
          </UButton>
        </div>
        <p
          v-else
          class="text-sm text-slate-400 line-clamp-2"
        >
          {{ recipe.content.slice(0, 100) }}...
        </p>
      </UCard>
    </div>
  </UContainer>
</template>
