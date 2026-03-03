// モジュールレベルの ref はすべての呼び出し元で共有されるシングルトン
const isGenerating = ref(false)
const isGenerationComplete = ref(false)

export const useGeneratingOverlay = () => {
  return { isGenerating, isGenerationComplete }
}
