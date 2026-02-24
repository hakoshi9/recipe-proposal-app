<script setup lang="ts">
const navItems = [
  { label: 'つくる', icon: 'i-ph-cooking-pot', to: '/' },
  { label: 'できた', icon: 'i-ph-clipboard-text', to: '/confirm' },
  { label: '保存', icon: 'i-ph-bookmark-simple', to: '/saved' },
]

const { initializeFromStorage } = useLocalStorage()

onMounted(() => {
  initializeFromStorage()
})
</script>

<template>
  <div>
    <!-- ヘッダー -->
    <header class="border-b border-amber-500 bg-amber-400 sticky top-0 z-50 shadow-md shadow-amber-200/60">
      <div class="container mx-auto px-4 h-14 flex items-center justify-between">
        <NuxtLink
          to="/"
          class="flex items-center gap-2"
        >
          <UIcon
            name="i-ph-cooking-pot"
            class="w-7 h-7 text-white drop-shadow-sm"
          />
          <span class="font-extrabold text-xl text-white drop-shadow-sm tracking-wide">こんだてAI</span>
        </NuxtLink>
      </div>
    </header>

    <!-- メインコンテンツ -->
    <main class="container mx-auto px-4 pb-20 sm:pb-8 pt-4">
      <slot />
    </main>

    <!-- モバイルボトムナビゲーション -->
    <nav class="fixed bottom-0 left-0 right-0 z-50 sm:hidden bg-white border-t border-amber-200 pb-safe shadow-[0_-2px_12px_0_rgba(245,158,11,0.10)]">
      <div class="flex justify-around items-center h-16 px-2">
        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex flex-col items-center gap-0.5 px-3 py-1.5 min-w-[4rem] rounded-2xl transition-all duration-200 text-slate-400 hover:text-amber-500"
          :class="[
            item.to === '/'
              ? '[&.router-link-exact-active]:text-amber-500 [&.router-link-exact-active]:bg-amber-50 [&.router-link-exact-active]:font-bold [&.router-link-exact-active]:scale-110'
              : '[&.router-link-active]:text-amber-500 [&.router-link-active]:bg-amber-50 [&.router-link-active]:font-bold [&.router-link-active]:scale-110'
          ]"
        >
          <UIcon
            :name="item.icon"
            class="w-5 h-5"
          />
          <span class="text-[10px] font-medium">{{ item.label }}</span>
        </NuxtLink>
      </div>
    </nav>
  </div>
</template>
