import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useRecipeStore } from '../../../app/stores/recipe'

describe('useRecipeStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  describe('初期状態', () => {
    it('ingredientsList が空文字で初期化される', () => {
      const store = useRecipeStore()
      expect(store.ingredientsList).toBe('')
    })

    it('recipeResult が空文字で初期化される', () => {
      const store = useRecipeStore()
      expect(store.recipeResult).toBe('')
    })

    it('savedRecipes が空配列で初期化される', () => {
      const store = useRecipeStore()
      expect(store.savedRecipes).toEqual([])
    })
  })

  describe('setIngredients', () => {
    it('食材テキストを更新できる', () => {
      const store = useRecipeStore()
      store.setIngredients('トマト、玉ねぎ')
      expect(store.ingredientsList).toBe('トマト、玉ねぎ')
    })

    it('空文字にリセットできる', () => {
      const store = useRecipeStore()
      store.setIngredients('トマト')
      store.setIngredients('')
      expect(store.ingredientsList).toBe('')
    })
  })

  describe('setRecipeResult', () => {
    it('レシピ結果テキストを更新できる', () => {
      const store = useRecipeStore()
      store.setRecipeResult('# トマトパスタ\n材料...')
      expect(store.recipeResult).toBe('# トマトパスタ\n材料...')
    })
  })

  describe('saveRecipe', () => {
    it('title と content を指定して savedRecipes に追加される', () => {
      const store = useRecipeStore()
      store.saveRecipe('パスタ', '# パスタ\n美味しいパスタのレシピ')
      expect(store.savedRecipes).toHaveLength(1)
      expect(store.savedRecipes[0]?.title).toBe('パスタ')
      expect(store.savedRecipes[0]?.content).toBe('# パスタ\n美味しいパスタのレシピ')
    })

    it('nutrition を省略して保存できる', () => {
      const store = useRecipeStore()
      store.saveRecipe('スープ', 'スープのレシピ')
      expect(store.savedRecipes[0]?.nutrition).toBeUndefined()
    })

    it('nutrition を指定して保存できる', () => {
      const store = useRecipeStore()
      store.saveRecipe('スープ', 'スープのレシピ', '- カロリー: 200kcal')
      expect(store.savedRecipes[0]?.nutrition).toBe('- カロリー: 200kcal')
    })

    it('保存されたレシピには日付が付く', () => {
      const store = useRecipeStore()
      store.saveRecipe('レシピ', 'コンテンツ')
      expect(store.savedRecipes[0]?.date).toMatch(/^\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}$/)
    })

    it('新しいレシピは先頭に追加される', () => {
      const store = useRecipeStore()
      store.saveRecipe('レシピ1', 'コンテンツ1')
      store.saveRecipe('レシピ2', 'コンテンツ2')
      expect(store.savedRecipes[0]?.content).toBe('コンテンツ2')
      expect(store.savedRecipes[1]?.content).toBe('コンテンツ1')
    })
  })

  describe('deleteRecipe', () => {
    it('指定インデックスのレシピを削除できる', () => {
      const store = useRecipeStore()
      store.saveRecipe('レシピA', 'コンテンツA')
      store.saveRecipe('レシピB', 'コンテンツB')
      // savedRecipes = [レシピB, レシピA]
      store.deleteRecipe(0)
      expect(store.savedRecipes).toHaveLength(1)
      expect(store.savedRecipes[0]?.content).toBe('コンテンツA')
    })
  })

  describe('persistToLocalStorage / restoreFromLocalStorage', () => {
    it('savedRecipes を localStorage に保存できる', () => {
      const store = useRecipeStore()
      store.saveRecipe('保存レシピ', '保存コンテンツ')
      store.persistToLocalStorage()

      const stored = localStorage.getItem('savedRecipes')
      expect(stored).not.toBeNull()
      const parsed = JSON.parse(stored!)
      expect(parsed[0].content).toBe('保存コンテンツ')
    })

    it('localStorage から savedRecipes を復元できる', () => {
      const recipes = [{ date: '2024/01/01 12:00', title: '復元レシピ', content: '復元テスト' }]
      localStorage.setItem('savedRecipes', JSON.stringify(recipes))

      const store = useRecipeStore()
      store.restoreFromLocalStorage()
      expect(store.savedRecipes).toHaveLength(1)
      expect(store.savedRecipes[0]?.content).toBe('復元テスト')
    })

    it('localStorage に不正なデータがあってもエラーにならない', () => {
      localStorage.setItem('savedRecipes', 'invalid json{{')
      const store = useRecipeStore()
      expect(() => store.restoreFromLocalStorage()).not.toThrow()
      expect(store.savedRecipes).toEqual([])
    })

    it('localStorage が空の場合は savedRecipes が変化しない', () => {
      const store = useRecipeStore()
      store.restoreFromLocalStorage()
      expect(store.savedRecipes).toEqual([])
    })
  })
})
