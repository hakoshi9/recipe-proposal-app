<script setup lang="ts">
/**
 * 広告表示用共通コンポーネント
 * Google AdSense の配置を想定。
 * featureAdsEnabled フラグが OFF の場合は非表示。
 * adsenseClientId が未設定の場合はプレースホルダーを表示する。
 */
interface Props {
  slotId?: string
  format?: 'auto' | 'fluid' | 'rectangle' | 'horizontal'
  class?: string
}

const props = defineProps<Props>()
const config = useRuntimeConfig()

const showAd = computed(() => config.public.featureAdsEnabled)
const hasClientId = computed(() => !!config.public.adsenseClientId)
</script>

<template>
  <div
    v-if="showAd"
    :class="[
      'ad-banner-container overflow-hidden transition-all duration-300',
      props.class
    ]"
  >
    <!-- adsenseClientId が設定されている場合は AdSense タグを配置 -->
    <!-- 現状はプレースホルダーとして実装。実運用時は ins タグに置き換える -->
    <div
      v-if="!hasClientId"
      class="bg-gray-50 border-2 border-dashed border-gray-200 flex flex-col items-center justify-center p-4 min-h-[90px] group hover:border-amber-300 transition-colors"
    >
      <div class="flex items-center gap-2 mb-1 opacity-40 group-hover:opacity-60 transition-opacity">
        <UIcon
          name="i-ph-megaphone-simple-duotone"
          class="w-5 h-5 text-gray-500"
        />
        <span class="text-xs font-semibold tracking-wider text-gray-500 uppercase">Sponsored</span>
      </div>
      <p class="text-xs text-gray-400">
        Advertisement Area
        <span
          v-if="props.slotId"
          class="block mt-0.5 opacity-70"
        >Slot: {{ props.slotId }}</span>
      </p>
    </div>

    <!-- Google AdSense 本番用（adsenseClientId 設定時）:
    <ins class="adsbygoogle"
         style="display:block"
         :data-ad-client="`ca-${config.public.adsenseClientId}`"
         :data-ad-slot="props.slotId"
         :data-ad-format="props.format ?? 'auto'"
         data-full-width-responsive="true"></ins>
    -->
  </div>
</template>

<style scoped>
.ad-banner-container {
  margin: 0;
}
</style>
