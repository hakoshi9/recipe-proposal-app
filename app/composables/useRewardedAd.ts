/**
 * useRewardedAd
 * リワード広告のモック実装（案ごとに個別管理）。
 * - 将来的に Google IMA SDK / AdSense Rewarded Ads への差し替えを前提とした抽象化インターフェース
 * - 現在はモーダル内で 5 秒カウントダウン後に解放
 * - 案ごとに個別で広告視聴が必要
 */
export const useRewardedAd = () => {
    /** 現在視聴中の案インデックス（-1 = 視聴していない） */
    const watchingIndex = ref(-1)
    const countdown = ref(0)
    /** 解放済みインデックスの Set */
    const unlockedSet = ref<Set<number>>(new Set())

    let timer: ReturnType<typeof setInterval> | null = null

    const _cleanup = () => {
        if (timer !== null) {
            clearInterval(timer)
            timer = null
        }
    }

    const isWatchingFor = (i: number) => watchingIndex.value === i
    const isUnlocked = (i: number) => unlockedSet.value.has(i)

    /**
     * 指定インデックスの広告視聴を開始する。
     * - モック: 5 秒カウントダウン
     * - 実装差し替え時はここの中身を SDK 呼び出しに置き換える
     * @returns Promise<boolean> 解放成功なら true
     */
    const watchAd = (index: number): Promise<boolean> => {
        return new Promise((resolve) => {
            _cleanup()
            watchingIndex.value = index
            countdown.value = 5

            timer = setInterval(() => {
                countdown.value -= 1
                if (countdown.value <= 0) {
                    _cleanup()
                    unlockedSet.value = new Set([...unlockedSet.value, index])
                    watchingIndex.value = -1
                    resolve(true)
                }
            }, 1000)
        })
    }

    /** セッションのロックをリセット（別レシピ生成時など） */
    const reset = () => {
        _cleanup()
        watchingIndex.value = -1
        countdown.value = 0
        unlockedSet.value = new Set()
    }

    return {
        watchingIndex,
        countdown,
        isWatchingFor,
        isUnlocked,
        watchAd,
        reset,
    }
}
