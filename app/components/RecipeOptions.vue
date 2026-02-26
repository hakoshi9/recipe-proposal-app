<script setup lang="ts">
const genre = defineModel<string>('genre', { required: true })
const numDishes = defineModel<number>('numDishes', { required: true })
const isChoi = defineModel<boolean>('isChoi', { required: true })
const useAll = defineModel<boolean>('useAll', { required: true })
const easyCooking = defineModel<boolean>('easyCooking', { required: true })
const extraRequest = defineModel<string>('extraRequest', { required: true })

const genres = [
  '一般的な料理',
  '離乳食(5-6ヶ月)',
  '離乳食(7-8ヶ月)',
  '離乳食(9-11ヶ月)',
  '離乳食(12-18ヶ月)',
]
</script>

<template>
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
        <USelect v-model="genre" :items="genres" />
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

      <div class="p-3 rounded-2xl bg-amber-50 border border-amber-200 space-y-2">
        <div class="text-xs font-bold uppercase tracking-wider text-amber-600 flex items-center gap-1">
          <UIcon name="i-ph-sparkle" class="w-3 h-3" />
          オプション
        </div>
        <UCheckbox v-model="isChoi" label="ちょい足しモード（+2〜3品）" />
        <UCheckbox v-model="useAll" label="全食材を使うモード" />
        <UCheckbox v-model="easyCooking" label="お手軽調理（15分以内）" />
      </div>

      <UAccordion :items="[{ label: '追加の要望（任意）', content: '' }]">
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
</template>
