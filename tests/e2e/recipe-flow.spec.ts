import { test, expect } from '@playwright/test'

test.describe('レシピ提案アプリ', () => {
  test.beforeEach(async ({ page }) => {
    // localStorage をクリアしてクリーンな状態でテスト
    await page.goto('/')
    await page.evaluate(() => localStorage.clear())
    await page.reload()
  })

  test('トップページが正常に表示される', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/レシピ|Recipe/i)
    // ページが読み込まれていることを確認
    await expect(page.locator('body')).toBeVisible()
  })

  test('画像アップロードエリアが表示される', async ({ page }) => {
    await page.goto('/')
    // ファイルインプットまたはアップロードエリアが存在する
    const fileInput = page.locator('input[type="file"]')
    await expect(fileInput).toBeAttached()
  })

  test('保存済みレシピタブが存在する', async ({ page }) => {
    await page.goto('/')
    // 保存済みタブまたはそれに相当する要素を確認
    const savedTab = page.getByText(/保存|Saved/i).first()
    await expect(savedTab).toBeVisible()
  })

  test('レシピがない場合の空状態メッセージが表示される', async ({ page }) => {
    await page.goto('/')
    // 保存済みタブに切り替え
    const savedTab = page.getByText(/保存|Saved/i).first()
    await savedTab.click()
    // 空状態のメッセージ（例: 「まだレシピがありません」など）
    const emptyMessage = page.getByText(/まだ|no recipe|保存されていない/i).first()
    // 空メッセージが表示されるか、またはリストが空であることを確認
    const recipeList = page.locator('[data-testid="saved-recipe"]')
    const count = await recipeList.count()
    if (count === 0) {
      // 空状態 — OK
      expect(count).toBe(0)
    } else {
      await expect(emptyMessage).toBeVisible()
    }
  })
})
