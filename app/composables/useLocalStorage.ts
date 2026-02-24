export const useLocalStorage = () => {
  const recipeStore = useRecipeStore()

  const initializeFromStorage = () => {
    recipeStore.restoreFromLocalStorage()
  }

  const saveToStorage = () => {
    recipeStore.persistToLocalStorage()
  }

  return {
    initializeFromStorage,
    saveToStorage,
  }
}
