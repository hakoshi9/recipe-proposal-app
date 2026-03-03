import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useRecipeStore } from '../../../app/stores/recipe'

// useLocalStorage は useRecipeStore() を Nuxt auto-import で参照しているため、
// ストアを直接テストすることで同等の挙動を検証する
describe('useLocalStorage (ストア経由でのテスト)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('initializeFromStorage: localStorage の内容をストアに復元する', () => {
    const recipes = [{ date: '2024/01/01 00:00', title: 'テストレシピ', content: 'テストレシピコンテンツ' }]
    localStorage.setItem('savedRecipes', JSON.stringify(recipes))

    const store = useRecipeStore()
    store.restoreFromLocalStorage()

    expect(store.savedRecipes).toHaveLength(1)
    expect(store.savedRecipes[0]?.content).toBe('テストレシピコンテンツ')
  })

  it('saveToStorage: ストアの savedRecipes を localStorage に書き込む', () => {
    const store = useRecipeStore()
    store.saveRecipe('保存するレシピ', '保存するコンテンツ')
    store.persistToLocalStorage()

    const raw = localStorage.getItem('savedRecipes')
    expect(raw).not.toBeNull()
    const parsed = JSON.parse(raw!)
    expect(parsed[0].content).toBe('保存するコンテンツ')
  })

  it('initializeFromStorage: localStorage が空の場合は何も変化しない', () => {
    const store = useRecipeStore()
    store.restoreFromLocalStorage()
    expect(store.savedRecipes).toEqual([])
  })

  it('saveToStorage → initializeFromStorage の往復で同じデータが得られる', () => {
    const store = useRecipeStore()
    store.saveRecipe('往復テスト', '往復コンテンツ')
    store.persistToLocalStorage()

    // 別のストアインスタンスで復元
    setActivePinia(createPinia())
    const store2 = useRecipeStore()
    store2.restoreFromLocalStorage()

    expect(store2.savedRecipes).toHaveLength(1)
    expect(store2.savedRecipes[0]?.content).toBe('往復コンテンツ')
  })
})
