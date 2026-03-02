import { describe, it, expect } from 'vitest'
import { useMarkdown } from '../../../app/composables/useMarkdown'

describe('useMarkdown', () => {
  const { renderMarkdown } = useMarkdown()

  describe('renderMarkdown', () => {
    it('空文字の場合は空文字を返す', () => {
      expect(renderMarkdown('')).toBe('')
    })

    it('見出しを HTML に変換する', () => {
      const result = renderMarkdown('# タイトル')
      expect(result).toContain('<h1>タイトル</h1>')
    })

    it('太字を HTML に変換する', () => {
      const result = renderMarkdown('**太字**')
      expect(result).toContain('<strong>太字</strong>')
    })

    it('斜体を HTML に変換する', () => {
      const result = renderMarkdown('*斜体*')
      expect(result).toContain('<em>斜体</em>')
    })

    it('箇条書きを HTML に変換する', () => {
      const result = renderMarkdown('- 項目1\n- 項目2')
      expect(result).toContain('<ul>')
      expect(result).toContain('<li>項目1</li>')
      expect(result).toContain('<li>項目2</li>')
    })

    it('改行 (GFM breaks) が <br> に変換される', () => {
      const result = renderMarkdown('1行目\n2行目')
      expect(result).toContain('<br>')
    })

    it('プレーンテキストをそのまま p タグで返す', () => {
      const result = renderMarkdown('シンプルなテキスト')
      expect(result).toContain('シンプルなテキスト')
    })

    it('文字列を返す（非同期にならない）', () => {
      const result = renderMarkdown('# テスト')
      expect(typeof result).toBe('string')
    })
  })
})
