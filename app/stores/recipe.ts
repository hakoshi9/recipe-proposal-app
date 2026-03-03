import { defineStore } from 'pinia'

export interface SavedRecipe {
  date: string
  title?: string
  content: string
  nutrition?: string
}

export const useRecipeStore = defineStore('recipe', {
  state: () => ({
    ingredientsList: '' as string,
    recipeResult: '' as string,
    savedRecipes: [] as SavedRecipe[],
  }),

  actions: {
    setIngredients(text: string) {
      this.ingredientsList = text
    },

    setRecipeResult(text: string) {
      this.recipeResult = text
    },

    saveRecipe(title: string, content: string, nutrition?: string) {
      const now = new Date()
      const date = `${now.getFullYear()}/${String(now.getMonth() + 1).padStart(2, '0')}/${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`

      this.savedRecipes.unshift({ date, title, content, nutrition })
      this.persistToLocalStorage()
    },

    updateRecipeTitle(index: number, title: string) {
      const recipe = this.savedRecipes[index]
      if (!recipe) return
      recipe.title = title
      this.persistToLocalStorage()
    },

    deleteRecipe(index: number) {
      this.savedRecipes.splice(index, 1)
      this.persistToLocalStorage()
    },

    persistToLocalStorage() {
      if (import.meta.client) {
        localStorage.setItem('savedRecipes', JSON.stringify(this.savedRecipes))
      }
    },

    restoreFromLocalStorage() {
      if (import.meta.client) {
        const stored = localStorage.getItem('savedRecipes')
        if (stored) {
          try {
            this.savedRecipes = JSON.parse(stored)
          } catch (e) {
            console.error('Failed to restore from localStorage:', e)
          }
        }
      }
    },
  },
})
