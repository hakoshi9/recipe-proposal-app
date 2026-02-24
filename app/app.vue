<script setup lang="ts">
useHead({
  link: [
    { rel: 'icon', href: '/favicon.ico' },
    { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
    { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap' },
  ],
  htmlAttrs: {
    lang: 'ja',
  },
})

const colorMode = useColorMode()
colorMode.preference = 'light'

const title = 'こんだてAI'
const description = '食材の写真を撮るだけ。AIがあなたの冷蔵庫にぴったりの献立を提案します。'

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description,
  twitterCard: 'summary_large_image',
})
</script>

<template>
  <UApp>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>
