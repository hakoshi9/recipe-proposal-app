import type { SavedRecipe } from '~/stores/recipe'

const APP_HASHTAG = '#こんだてAI'

function buildTweetText(title: string): string {
  return `AIが提案したレシピ「${title}」を試してみました！✨ ${APP_HASHTAG}`
}

function getDisplayTitle(recipe: SavedRecipe): string {
  return (recipe.title ?? 'レシピ').replace(/^案[A-CＡ-Ｃ][:：]\s*/, '').trim() || 'レシピ'
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

async function generateRecipeImage(recipe: SavedRecipe): Promise<Blob> {
  const [{ default: html2canvas }, { createApp, nextTick }] = await Promise.all([
    import('html2canvas'),
    import('vue'),
  ])
  const { default: RecipeShareCard } = await import('~/components/RecipeShareCard.vue')

  const container = document.createElement('div')
  container.style.cssText = 'position:fixed;left:-9999px;top:0;z-index:-9999;pointer-events:none;'
  document.body.appendChild(container)

  const app = createApp(RecipeShareCard, { recipe })
  app.mount(container)

  await nextTick()
  // Ensure fonts and layout are settled
  await new Promise<void>(resolve => setTimeout(resolve, 150))

  const el = container.firstElementChild as HTMLElement
  const canvas = await html2canvas(el, {
    useCORS: true,
    scale: 2,
    backgroundColor: '#ffffff',
    logging: false,
    width: el.offsetWidth,
    height: el.offsetHeight,
  })

  app.unmount()
  document.body.removeChild(container)

  return new Promise<Blob>((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob)
      else reject(new Error('画像の生成に失敗しました'))
    }, 'image/png')
  })
}

export function useShareToX() {
  const toast = useToast()
  const isSharing = ref(false)

  async function shareToX(recipe: SavedRecipe): Promise<void> {
    if (isSharing.value) return
    isSharing.value = true

    try {
      const blob = await generateRecipeImage(recipe)
      const title = getDisplayTitle(recipe)
      const tweetText = buildTweetText(title)
      const imageFile = new File([blob], 'kondateai_recipe.png', { type: 'image/png' })

      // モバイル: Web Share API でXアプリへ直接シェア
      if (navigator.canShare?.({ files: [imageFile] })) {
        await navigator.share({
          files: [imageFile],
          text: tweetText,
        })
      }
      else {
        // PC・フォールバック: 画像をダウンロード + Twitter Web Intent を開く
        downloadBlob(blob, `kondateai_${Date.now()}.png`)
        const intentUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(tweetText)}`
        window.open(intentUrl, '_blank', 'noopener,noreferrer')
        toast.add({
          title: '画像をダウンロードしました',
          description: 'Xの投稿画面で画像を添付してください',
          icon: 'i-ph-download-simple',
          color: 'success',
          duration: 6000,
        })
      }
    }
    catch (err) {
      // ユーザーがキャンセルした場合は何もしない
      if (err instanceof Error && err.name !== 'AbortError') {
        toast.add({
          title: '共有に失敗しました',
          description: 'もう一度お試しください',
          icon: 'i-ph-warning-circle',
          color: 'error',
        })
      }
    }
    finally {
      isSharing.value = false
    }
  }

  return { shareToX, isSharing }
}
