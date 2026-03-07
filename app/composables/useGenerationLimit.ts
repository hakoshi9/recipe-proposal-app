/**
 * useGenerationLimit
 * 1日あたりのレシピ生成回数を localStorage で管理するコンポーザブル。
 * - キー: recipe_gen_date  / recipe_gen_count
 * - 日付が変わった場合はカウントをリセット
 */
export const useGenerationLimit = () => {
    const DAILY_LIMIT = 5
    const DATE_KEY = 'recipe_gen_date'
    const COUNT_KEY = 'recipe_gen_count'

    const todayStr = () => new Date().toLocaleDateString('sv-SE') // "YYYY-MM-DD"

    const _getCount = (): number => {
        if (import.meta.server) return 0
        const savedDate = localStorage.getItem(DATE_KEY)
        if (savedDate !== todayStr()) {
            // 日付が変わったらリセット
            localStorage.setItem(DATE_KEY, todayStr())
            localStorage.setItem(COUNT_KEY, '0')
            return 0
        }
        return parseInt(localStorage.getItem(COUNT_KEY) ?? '0', 10)
    }

    const remaining = ref(DAILY_LIMIT - _getCount())
    const isLimitReached = computed(() => remaining.value <= 0)

    /** 生成時に呼び出す。上限に達していれば false を返す */
    const consume = (): boolean => {
        if (import.meta.server) return true
        const count = _getCount()
        if (count >= DAILY_LIMIT) {
            remaining.value = 0
            return false
        }
        const newCount = count + 1
        localStorage.setItem(COUNT_KEY, String(newCount))
        remaining.value = DAILY_LIMIT - newCount
        return true
    }

    return {
        DAILY_LIMIT,
        remaining,
        isLimitReached,
        consume,
    }
}
