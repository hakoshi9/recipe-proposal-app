<script setup lang="ts">
import { getExifOrientation, applyExifOrientation } from '~/composables/useExifOrientation'

const props = defineProps<{
  isIdentifying: boolean
}>()

const emit = defineEmits<{
  'identify': [base64Images: string[]]
}>()

const MAX_IMAGES = 5

const files = ref<File[]>([])
const previews = ref<string[]>([])
const fileInputRef = ref<HTMLInputElement>()
const cameraInputRef = ref<HTMLInputElement>()

const isAtMaxImages = computed(() => files.value.length >= MAX_IMAGES)

const addPreview = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    if (e.target?.result) {
      previews.value.push(e.target.result as string)
    }
  }
  reader.readAsDataURL(file)
}

const handleFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (!input.files) return
  const remaining = MAX_IMAGES - files.value.length
  const newFiles = Array.from(input.files).slice(0, remaining)
  for (const file of newFiles) {
    files.value.push(file)
    addPreview(file)
  }
}

const handleCameraCapture = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (!input.files || !input.files[0]) return
  if (isAtMaxImages.value) return
  const file = input.files[0]
  files.value.push(file)
  addPreview(file)
  // 同じ写真でも再撮影できるようにリセット
  input.value = ''
}

const removeImage = (index: number) => {
  files.value.splice(index, 1)
  previews.value.splice(index, 1)
}

const resizeImageToBase64 = async (file: File): Promise<string> => {
  const orientation = await getExifOrientation(file)
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (event) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        let width = img.width
        let height = img.height
        const maxSize = 1024

        if (Math.max(width, height) > maxSize) {
          const ratio = maxSize / Math.max(width, height)
          width = Math.round(width * ratio)
          height = Math.round(height * ratio)
        }

        const ctx = canvas.getContext('2d')!
        const [outWidth, outHeight] = applyExifOrientation(ctx, orientation, width, height)
        canvas.width = outWidth
        canvas.height = outHeight

        ctx.drawImage(img, 0, 0, width, height)
        const dataUrl = canvas.toDataURL('image/jpeg', 0.85)
        resolve(dataUrl.split(',')[1])
      }
      img.src = event.target?.result as string
    }
    reader.readAsDataURL(file)
  })
}

const onIdentify = async () => {
  const base64Images: string[] = []
  for (const file of files.value) {
    base64Images.push(await resizeImageToBase64(file))
  }
  emit('identify', base64Images)
}
</script>

<template>
  <div class="p-3 rounded-2xl bg-gray-50 border border-gray-200 space-y-3">
    <div class="text-xs font-bold uppercase tracking-wider text-gray-500 flex items-center gap-1 justify-between">
      <div class="flex items-center gap-1">
        <UIcon name="i-ph-camera" class="w-3 h-3" />
        写真から読み取り
      </div>
      <span class="text-xs font-semibold" :class="isAtMaxImages ? 'text-red-400' : 'text-gray-400'">
        {{ files.length }}/{{ MAX_IMAGES }}枚
      </span>
    </div>

    <div class="flex gap-2">
      <!-- ギャラリー選択 -->
      <div
        class="flex-1 border-2 border-dashed border-amber-200 rounded-xl p-3 text-center cursor-pointer hover:border-amber-400 hover:bg-amber-50/50 transition-all"
        :class="isAtMaxImages ? 'opacity-40 pointer-events-none' : ''"
        @click="fileInputRef?.click()"
      >
        <UIcon name="i-ph-image-square" class="w-6 h-6 text-amber-300 mx-auto mb-1" />
        <p class="text-xs font-medium text-slate-500">ギャラリー</p>
        <input
          ref="fileInputRef"
          type="file"
          multiple
          accept="image/*"
          class="hidden"
          @change="handleFileChange"
        />
      </div>

      <!-- カメラ直接起動 -->
      <div
        class="flex-1 border-2 border-dashed border-sky-200 rounded-xl p-3 text-center cursor-pointer hover:border-sky-400 hover:bg-sky-50/50 transition-all"
        :class="isAtMaxImages ? 'opacity-40 pointer-events-none' : ''"
        @click="cameraInputRef?.click()"
      >
        <UIcon name="i-ph-camera" class="w-6 h-6 text-sky-300 mx-auto mb-1" />
        <p class="text-xs font-medium text-slate-500">カメラ撮影</p>
        <input
          ref="cameraInputRef"
          type="file"
          accept="image/*"
          capture="environment"
          class="hidden"
          @change="handleCameraCapture"
        />
      </div>
    </div>

    <!-- 上限メッセージ -->
    <p v-if="isAtMaxImages" class="text-xs text-red-400 text-center font-medium">
      上限（{{ MAX_IMAGES }}枚）に達しました。不要な写真を削除してから追加してください。
    </p>

    <!-- プレビュー -->
    <div v-if="previews.length" class="grid grid-cols-4 gap-2">
      <div v-for="(src, i) in previews" :key="i" class="relative animate-pop-in">
        <img :src="src" class="w-full h-20 object-cover rounded-xl border border-amber-100" />
        <button
          type="button"
          class="absolute -top-1.5 -right-1.5 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs shadow-sm"
          @click="removeImage(i)"
        >
          ×
        </button>
      </div>
    </div>

    <!-- 食材読み取りボタン -->
    <UButton
      v-if="files.length > 0"
      :loading="isIdentifying"
      color="neutral"
      variant="soft"
      size="sm"
      block
      icon="i-ph-magnifying-glass"
      class="font-bold"
      @click="onIdentify"
    >
      写真から食材を読み取る
    </UButton>
  </div>
</template>
