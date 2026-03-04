import type { SavedRecipe } from '~/stores/recipe'

// ── 定数 ────────────────────────────────────────────────
const APP_HASHTAG = '#こんだてAI'
const APP_SUBTITLE = 'AIが提案するレシピアプリ'

const CARD_W = 800
const SCALE = 2
const PAD = 28
const HEADER_H = 76
const FOOTER_H = 44

const COLOR_AMBER = '#FBBF24'
const COLOR_BODY_BG = '#FFFBEB'
const COLOR_DIVIDER = '#FDE68A'
const COLOR_TITLE = '#1E293B'
const COLOR_CONTENT = '#475569'
const COLOR_WHITE = '#ffffff'
const COLOR_WHITE_SOFT = 'rgba(255,255,255,0.9)'

const FONT = '"Noto Sans JP","Hiragino Sans","Yu Gothic","Meiryo",sans-serif'

// ── ユーティリティ ────────────────────────────────────────
function getDisplayTitle(recipe: SavedRecipe): string {
  return (recipe.title ?? 'レシピ').replace(/^案[A-CＡ-Ｃ][:：]\s*/, '').trim() || 'レシピ'
}

function buildTweetText(title: string): string {
  return `AIが提案したレシピ「${title}」を試してみました！✨ ${APP_HASHTAG}`
}

function stripMarkdown(md: string): string {
  return md
    .replace(/^#{1,6}\s+(.+)$/gm, '【$1】')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/^\s*[-*+]\s+/gm, '• ')
    .replace(/^\s*(\d+)\.\s+/gm, '$1. ')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

/** 文字単位で折り返す（日本語対応）*/
function wrapText(ctx: CanvasRenderingContext2D, text: string, maxWidth: number): string[] {
  const result: string[] = []
  for (const para of text.split('\n')) {
    if (!para.trim()) {
      result.push('')
      continue
    }
    let line = ''
    for (const ch of para) {
      if (ctx.measureText(line + ch).width > maxWidth && line.length > 0) {
        result.push(line)
        line = ch
      }
      else {
        line += ch
      }
    }
    if (line) result.push(line)
  }
  return result
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

// ── Canvas 描画 ───────────────────────────────────────────
async function generateRecipeImage(recipe: SavedRecipe): Promise<Blob> {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('Canvas not supported')

  const title = getDisplayTitle(recipe)
  const contentText = stripMarkdown(recipe.content)

  // テキスト計測（スケール前）
  const TITLE_FONT = `800 24px ${FONT}`
  const CONTENT_FONT = `400 13px ${FONT}`

  ctx.font = TITLE_FONT
  const titleLines = wrapText(ctx, title, CARD_W - PAD * 2)
  const TITLE_LINE_H = 33
  const titleBlockH = titleLines.length * TITLE_LINE_H

  ctx.font = CONTENT_FONT
  const allContentLines = wrapText(ctx, contentText, CARD_W - PAD * 2)
  const CONTENT_LINE_H = 22
  const MAX_CONTENT_LINES = 50
  const shownLines = allContentLines.slice(0, MAX_CONTENT_LINES)
  const contentBlockH = shownLines.length * CONTENT_LINE_H

  // 高さ計算
  const bodyH = PAD + titleBlockH + 14 + 2 + 16 + contentBlockH + PAD
  const totalH = HEADER_H + bodyH + FOOTER_H

  // Canvas セットアップ
  canvas.width = CARD_W * SCALE
  canvas.height = totalH * SCALE
  ctx.scale(SCALE, SCALE)
  ctx.textBaseline = 'top'

  // ── ヘッダー ──
  ctx.fillStyle = COLOR_AMBER
  ctx.fillRect(0, 0, CARD_W, HEADER_H)

  ctx.fillStyle = COLOR_WHITE
  ctx.font = `800 21px ${FONT}`
  ctx.fillText('🍳  こんだてAI', PAD, 18)

  ctx.fillStyle = COLOR_WHITE_SOFT
  ctx.font = `400 11px ${FONT}`
  ctx.fillText(APP_SUBTITLE, PAD, 48)

  // ── ボディ ──
  ctx.fillStyle = COLOR_BODY_BG
  ctx.fillRect(0, HEADER_H, CARD_W, bodyH)

  let y = HEADER_H + PAD

  // タイトル
  ctx.font = TITLE_FONT
  ctx.fillStyle = COLOR_TITLE
  for (const line of titleLines) {
    ctx.fillText(line, PAD, y)
    y += TITLE_LINE_H
  }

  // 区切り線
  y += 14
  ctx.fillStyle = COLOR_DIVIDER
  ctx.fillRect(PAD, y, CARD_W - PAD * 2, 2)
  y += 18

  // コンテンツ
  ctx.font = CONTENT_FONT
  ctx.fillStyle = COLOR_CONTENT
  for (const line of shownLines) {
    ctx.fillText(line, PAD, y)
    y += CONTENT_LINE_H
  }

  // ── フッター ──
  const footerY = HEADER_H + bodyH
  ctx.fillStyle = COLOR_AMBER
  ctx.fillRect(0, footerY, CARD_W, FOOTER_H)

  ctx.textBaseline = 'middle'
  const footerMidY = footerY + FOOTER_H / 2

  ctx.fillStyle = COLOR_WHITE
  ctx.font = `700 13px ${FONT}`
  ctx.textAlign = 'left'
  ctx.fillText(APP_HASHTAG, PAD, footerMidY)

  ctx.fillStyle = COLOR_WHITE_SOFT
  ctx.font = `400 12px ${FONT}`
  ctx.textAlign = 'right'
  ctx.fillText(recipe.date, CARD_W - PAD, footerMidY)

  return new Promise<Blob>((resolve, reject) => {
    canvas.toBlob(
      blob => blob ? resolve(blob) : reject(new Error('画像の生成に失敗しました')),
      'image/png',
    )
  })
}

// ── コンポーザブル ────────────────────────────────────────
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
      if (typeof navigator.share === 'function' && navigator.canShare?.({ files: [imageFile] })) {
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
      // ユーザーキャンセルは無視
      if (err instanceof Error && err.name !== 'AbortError') {
        console.error('[useShareToX]', err)
        toast.add({
          title: '共有に失敗しました',
          description: err.message || 'もう一度お試しください',
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
