// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',

  future: {
    compatibilityVersion: 4,
  },

  modules: [
    '@nuxt/ui',
    '@pinia/nuxt',
  ],

  ssr: false,

  app: {
    pageTransition: { name: 'page', mode: 'out-in' },
  },

  css: [
    '~/assets/css/main.css',
  ],

  colorMode: {
    preference: 'light',
    fallback: 'light',
  },

  runtimeConfig: {
    geminiApiKey: process.env.GEMINI_API_KEY || '',
  },

  devtools: { enabled: true },

  vite: {
    server: {
      allowedHosts: true,
    },
  },
})
