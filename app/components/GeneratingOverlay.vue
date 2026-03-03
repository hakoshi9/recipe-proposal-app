<script setup lang="ts">
defineProps<{
  completed?: boolean
}>()

const messages = [
  { icon: 'i-ph-sparkle', text: 'AIがレシピを考案しています...' },
  { icon: 'i-ph-carrot', text: '食材の相性を分析中...' },
  { icon: 'i-ph-cooking-pot', text: '料理の手順を考えています...' },
  { icon: 'i-ph-fork-knife', text: 'おいしいレシピを模索中...' },
]

const currentIndex = ref(0)

let timer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  timer = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % messages.length
  }, 3000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

const current = computed(() => messages[currentIndex.value])
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex flex-col items-center justify-center gap-10"
      style="background: rgba(255, 252, 240, 0.92); backdrop-filter: blur(8px);"
    >
      <Transition name="state-switch" mode="out-in">
        <!-- 完了状態 -->
        <div v-if="completed" key="complete" class="flex flex-col items-center gap-8">
          <div class="relative flex items-center justify-center w-32 h-32">
            <div class="absolute inset-0 rounded-full bg-amber-200 animate-ping opacity-30" />
            <div class="complete-ring absolute inset-0 rounded-full border-4 border-amber-400" />
            <div class="flex items-center justify-center w-20 h-20 rounded-full bg-amber-100 shadow-lg shadow-amber-200">
              <UIcon name="i-ph-check-circle" class="w-10 h-10 text-amber-500 complete-icon" />
            </div>
          </div>
          <div class="text-center space-y-2 px-8">
            <p class="text-xl font-bold text-slate-700">レシピが完成しました！</p>
            <p class="text-sm text-slate-400">レシピ画面に移動します</p>
          </div>
        </div>

        <!-- ローディング状態 -->
        <div v-else key="loading" class="flex flex-col items-center gap-8">
          <!-- アイコン + 回転リング -->
          <div class="relative flex items-center justify-center w-32 h-32">
            <div class="absolute inset-0 rounded-full border-4 border-amber-100 border-t-amber-400 animate-spin" />
            <div class="absolute inset-3 rounded-full bg-amber-200 animate-ping opacity-25" />
            <div class="relative flex items-center justify-center w-20 h-20 rounded-full bg-amber-100 shadow-lg shadow-amber-200">
              <Transition name="icon-bounce" mode="out-in">
                <UIcon
                  :key="current.icon"
                  :name="current.icon"
                  class="w-10 h-10 text-amber-500"
                />
              </Transition>
            </div>
          </div>

          <!-- メッセージ -->
          <div class="text-center space-y-2 px-8">
            <Transition name="msg-slide" mode="out-in">
              <p
                :key="current.text"
                class="text-lg font-bold text-slate-700"
              >
                {{ current.text }}
              </p>
            </Transition>
            <p class="text-sm text-slate-400">レシピができあがるまで少々お待ちください</p>
          </div>

        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<style scoped>
/* ローディング↔完了の切り替えトランジション */
.state-switch-enter-active {
  transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.state-switch-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease-in;
}
.state-switch-enter-from {
  opacity: 0;
  transform: scale(0.85);
}
.state-switch-leave-to {
  opacity: 0;
  transform: scale(0.85);
}

/* 完了時のアイコンポップイン */
.complete-icon {
  animation: complete-pop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
@keyframes complete-pop {
  0% { transform: scale(0) rotate(-20deg); opacity: 0; }
  100% { transform: scale(1) rotate(0deg); opacity: 1; }
}

/* 完了時のリングエフェクト */
.complete-ring {
  animation: ring-expand 0.6s ease-out forwards;
}
@keyframes ring-expand {
  0% { transform: scale(0.6); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

/* アイコン切り替えアニメーション */
.icon-bounce-enter-active {
  transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.icon-bounce-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease-in;
}
.icon-bounce-enter-from {
  opacity: 0;
  transform: scale(0.4) rotate(-25deg);
}
.icon-bounce-leave-to {
  opacity: 0;
  transform: scale(0.4) rotate(25deg);
}

/* メッセージスライドアニメーション */
.msg-slide-enter-active,
.msg-slide-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.msg-slide-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.msg-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
