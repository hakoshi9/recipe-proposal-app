import { marked } from 'marked'

marked.setOptions({
  breaks: true,
  gfm: true,
})

export function useMarkdown() {
  const renderMarkdown = (text: string): string => {
    if (!text) return ''
    return marked.parse(text, { async: false }) as string
  }

  return { renderMarkdown }
}
