<script setup lang="ts">
const messages = [
  { icon: 'i-ph-sparkle', text: 'AIがレシピを考案しています...' },
  { icon: 'i-ph-carrot', text: '食材の組み合わせを検討中...' },
  { icon: 'i-ph-cooking-pot', text: '料理の手順を整理しています...' },
  { icon: 'i-ph-check-circle', text: 'もうすぐ完成します！' },
]

const currentIndex = ref(0)

let timer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  timer = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % messages.length
  }, 4000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

const current = computed(() => messages[currentIndex.value])
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex flex-col items-center justify-center gap-8"
      style="background: rgba(255, 252, 240, 0.92); backdrop-filter: blur(8px);"
    >
      <!-- アイコンアニメーション -->
      <div class="relative flex items-center justify-center w-24 h-24">
        <div class="absolute inset-0 rounded-full bg-amber-100 animate-ping opacity-40" />
        <div class="relative flex items-center justify-center w-20 h-20 rounded-full bg-amber-100 shadow-lg shadow-amber-200">
          <Transition name="icon-fade" mode="out-in">
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
        <Transition name="msg-fade" mode="out-in">
          <p
            :key="current.text"
            class="text-lg font-bold text-slate-700"
          >
            {{ current.text }}
          </p>
        </Transition>
        <p class="text-sm text-slate-400">しばらくお待ちください</p>
      </div>

      <!-- ドットインジケーター -->
      <div class="flex gap-2">
        <div
          v-for="(_, i) in messages"
          :key="i"
          class="w-2 h-2 rounded-full transition-all duration-500"
          :class="i === currentIndex ? 'bg-amber-400 w-5' : 'bg-amber-200'"
        />
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.icon-fade-enter-active,
.icon-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.icon-fade-enter-from {
  opacity: 0;
  transform: scale(0.7) rotate(-10deg);
}
.icon-fade-leave-to {
  opacity: 0;
  transform: scale(0.7) rotate(10deg);
}

.msg-fade-enter-active,
.msg-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.msg-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.msg-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
