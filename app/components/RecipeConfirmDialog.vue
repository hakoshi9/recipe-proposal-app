<script setup lang="ts">
const props = defineProps<{
  open: boolean
  genre: string
  numDishes: number
  isChoi: boolean
  useAll: boolean
  easyCooking: boolean
  extraRequest: string
  ingredientsText: string
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const ingredientLines = computed(() =>
  props.ingredientsText.trim().split('\n').filter(l => l.trim()),
)

const activeOptions = computed(() => [
  props.isChoi && 'ちょい足しモード',
  props.useAll && '全食材を使うモード',
  props.easyCooking && 'お手軽調理（15分以内）',
].filter(Boolean) as string[])
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog-backdrop">
      <div v-if="open" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
        <!-- 背景 -->
        <div
          class="absolute inset-0 bg-black/30 backdrop-blur-sm"
          @click="emit('cancel')"
        />

        <!-- ダイアログ本体 -->
        <Transition name="dialog-sheet">
          <div
            v-if="open"
            class="relative w-full max-w-sm mx-4 mb-4 sm:mb-0 bg-white rounded-2xl shadow-2xl overflow-hidden"
          >
            <!-- ヘッダー -->
            <div class="flex items-center gap-2 px-5 pt-5 pb-3 border-b border-slate-100">
              <UIcon name="i-ph-clipboard-text" class="w-5 h-5 text-amber-500 shrink-0" />
              <h2 class="font-bold text-slate-800">この条件でレシピを考えてもらう？</h2>
            </div>

            <!-- 設定サマリー -->
            <div class="px-5 py-4 space-y-3 max-h-[60vh] overflow-y-auto">
              <!-- ジャンル・品数 -->
              <div class="flex gap-2 flex-wrap">
                <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-amber-100 text-amber-700 text-sm font-semibold">
                  <UIcon name="i-ph-tag" class="w-3.5 h-3.5" />
                  {{ genre }}
                </span>
                <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-amber-100 text-amber-700 text-sm font-semibold">
                  <UIcon name="i-ph-fork-knife" class="w-3.5 h-3.5" />
                  {{ numDishes }}品
                </span>
              </div>

              <!-- オプション -->
              <div v-if="activeOptions.length" class="space-y-1">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-wide">オプション</p>
                <div class="flex flex-wrap gap-1.5">
                  <span
                    v-for="opt in activeOptions"
                    :key="opt"
                    class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-sky-100 text-sky-700 text-xs font-semibold"
                  >
                    <UIcon name="i-ph-check" class="w-3 h-3" />
                    {{ opt }}
                  </span>
                </div>
              </div>

              <!-- 追加の要望 -->
              <div v-if="extraRequest.trim()">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-wide mb-1">追加の要望</p>
                <p class="text-sm text-slate-600 bg-slate-50 rounded-lg px-3 py-2 leading-relaxed">
                  {{ extraRequest }}
                </p>
              </div>

              <!-- 食材 -->
              <div>
                <p class="text-xs font-bold text-slate-400 uppercase tracking-wide mb-1">
                  食材（{{ ingredientLines.length }}種）
                </p>
                <div class="bg-amber-50 rounded-lg px-3 py-2 space-y-0.5">
                  <p
                    v-for="(line, i) in ingredientLines.slice(0, 6)"
                    :key="i"
                    class="text-sm text-slate-700"
                  >
                    {{ line }}
                  </p>
                  <p v-if="ingredientLines.length > 6" class="text-xs text-slate-400">
                    ...他 {{ ingredientLines.length - 6 }} 種
                  </p>
                </div>
              </div>
            </div>

            <!-- アクションボタン -->
            <div class="flex gap-3 px-5 py-4 border-t border-slate-100">
              <UButton
                color="neutral"
                variant="soft"
                class="flex-1"
                icon="i-ph-arrow-left"
                @click="emit('cancel')"
              >
                戻る
              </UButton>
              <UButton
                color="primary"
                class="flex-1 font-extrabold shadow-md shadow-amber-200"
                icon="i-ph-sparkle"
                @click="emit('confirm')"
              >
                レシピを考えて！
              </UButton>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.dialog-backdrop-enter-active,
.dialog-backdrop-leave-active {
  transition: opacity 0.25s ease;
}
.dialog-backdrop-enter-from,
.dialog-backdrop-leave-to {
  opacity: 0;
}

.dialog-sheet-enter-active {
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.dialog-sheet-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease-in;
}
.dialog-sheet-enter-from {
  opacity: 0;
  transform: translateY(24px) scale(0.97);
}
.dialog-sheet-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.97);
}
</style>
