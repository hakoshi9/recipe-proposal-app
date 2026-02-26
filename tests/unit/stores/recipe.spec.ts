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
    it('recipeResult が空の場合は保存しない', () => {
      const store = useRecipeStore()
      store.saveRecipe()
      expect(store.savedRecipes).toHaveLength(0)
    })

    it('recipeResult がある場合は savedRecipes に追加される', () => {
      const store = useRecipeStore()
      store.setRecipeResult('# パスタ\n美味しいパスタのレシピ')
      store.saveRecipe()
      expect(store.savedRecipes).toHaveLength(1)
      expect(store.savedRecipes[0].content).toBe('# パスタ\n美味しいパスタのレシピ')
    })

    it('保存されたレシピには日付が付く', () => {
      const store = useRecipeStore()
      store.setRecipeResult('レシピ')
      store.saveRecipe()
      expect(store.savedRecipes[0].date).toMatch(/^\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}$/)
    })

    it('新しいレシピは先頭に追加される', () => {
      const store = useRecipeStore()
      store.setRecipeResult('レシピ1')
      store.saveRecipe()
      store.setRecipeResult('レシピ2')
      store.saveRecipe()
      expect(store.savedRecipes[0].content).toBe('レシピ2')
      expect(store.savedRecipes[1].content).toBe('レシピ1')
    })
  })

  describe('deleteRecipe', () => {
    it('指定インデックスのレシピを削除できる', () => {
      const store = useRecipeStore()
      store.setRecipeResult('レシピA')
      store.saveRecipe()
      store.setRecipeResult('レシピB')
      store.saveRecipe()
      // savedRecipes = [レシピB, レシピA]
      store.deleteRecipe(0)
      expect(store.savedRecipes).toHaveLength(1)
      expect(store.savedRecipes[0].content).toBe('レシピA')
    })
  })

  describe('persistToLocalStorage / restoreFromLocalStorage', () => {
    it('savedRecipes を localStorage に保存できる', () => {
      const store = useRecipeStore()
      store.setRecipeResult('保存レシピ')
      store.saveRecipe()
      store.persistToLocalStorage()

      const stored = localStorage.getItem('savedRecipes')
      expect(stored).not.toBeNull()
      const parsed = JSON.parse(stored!)
      expect(parsed[0].content).toBe('保存レシピ')
    })

    it('localStorage から savedRecipes を復元できる', () => {
      const recipes = [{ date: '2024/01/01 12:00', content: '復元テスト' }]
      localStorage.setItem('savedRecipes', JSON.stringify(recipes))

      const store = useRecipeStore()
      store.restoreFromLocalStorage()
      expect(store.savedRecipes).toHaveLength(1)
      expect(store.savedRecipes[0].content).toBe('復元テスト')
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
