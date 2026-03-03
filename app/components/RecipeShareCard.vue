<script setup lang="ts">
import type { SavedRecipe } from '~/stores/recipe'

const props = defineProps<{ recipe: SavedRecipe }>()

const displayTitle = computed(() => {
  return (props.recipe.title ?? 'レシピ').replace(/^案[A-CＡ-Ｃ][:：]\s*/, '').trim() || 'レシピ'
})

const contentPreview = computed(() => {
  return props.recipe.content
    .replace(/^#{1,6}\s+(.+)$/gm, '▍$1')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/^\s*[-*+]\s+/gm, '• ')
    .replace(/^\s*(\d+)\.\s+/gm, '$1. ')
    .replace(/\n{3,}/g, '\n\n')
    .slice(0, 480)
    .trim()
})
</script>

<template>
  <div
    style="
      width: 800px;
      background: #ffffff;
      font-family: 'Noto Sans JP', 'Hiragino Sans', 'Yu Gothic', sans-serif;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-sizing: border-box;
    "
  >
    <!-- ヘッダー -->
    <div
      style="
        background: #FBBF24;
        padding: 18px 28px;
        display: flex;
        align-items: center;
        gap: 12px;
        flex-shrink: 0;
      "
    >
      <div
        style="
          width: 44px;
          height: 44px;
          background: rgba(255, 255, 255, 0.25);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 22px;
          flex-shrink: 0;
        "
      >
        🍳
      </div>
      <div>
        <div
          style="
            font-weight: 800;
            font-size: 22px;
            color: white;
            letter-spacing: 0.02em;
            line-height: 1.2;
          "
        >
          こんだてAI
        </div>
        <div style="font-size: 11px; color: rgba(255, 255, 255, 0.9); margin-top: 2px;">
          AIが提案するレシピアプリ
        </div>
      </div>
    </div>

    <!-- ボディ -->
    <div style="flex: 1; padding: 28px 28px 24px; background: #FFFBEB;">
      <!-- レシピタイトル -->
      <div
        style="
          font-weight: 800;
          font-size: 26px;
          color: #1E293B;
          margin-bottom: 14px;
          line-height: 1.4;
        "
      >
        {{ displayTitle }}
      </div>

      <!-- デコライン -->
      <div style="height: 2px; background: #FDE68A; margin-bottom: 16px;" />

      <!-- レシピ内容プレビュー -->
      <div
        style="
          font-size: 13px;
          color: #475569;
          white-space: pre-wrap;
          line-height: 1.85;
          overflow: hidden;
          max-height: 340px;
        "
      >{{ contentPreview }}</div>
    </div>

    <!-- フッター -->
    <div
      style="
        background: #FBBF24;
        padding: 11px 28px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-shrink: 0;
      "
    >
      <span style="font-size: 13px; font-weight: 700; color: white;">#こんだてAI</span>
      <span style="font-size: 12px; color: rgba(255, 255, 255, 0.9);">{{ recipe.date }}</span>
    </div>
  </div>
</template>
