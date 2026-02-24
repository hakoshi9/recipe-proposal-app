import { GoogleGenerativeAI } from '@google/generative-ai'
import { buildCacheKey, getCacheEntry, setCacheEntry } from '../utils/recipeCache'

interface RecipeRequest {
  ingredients: string
  mode: string
  numDishes: number
  isChoi: boolean
  useAll: boolean
  extraRequest: string
  easyCooking: boolean
  bypassCache?: boolean
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const body = await readBody<RecipeRequest>(event)

  if (!body.ingredients) {
    throw createError({ statusCode: 400, statusMessage: '食材が指定されていません' })
  }

  setResponseHeader(event, 'Content-Type', 'text/event-stream')
  setResponseHeader(event, 'Cache-Control', 'no-cache')
  setResponseHeader(event, 'Connection', 'keep-alive')

  const encoder = new TextEncoder()

  // キャッシュ対象判定: extraRequest が空の場合のみ
  const isCacheable = !body.extraRequest?.trim()
  const cacheKey = isCacheable ? buildCacheKey({
    ingredients: body.ingredients,
    mode: body.mode,
    numDishes: body.numDishes,
    isChoi: body.isChoi,
    useAll: body.useAll,
    easyCooking: body.easyCooking,
  }) : null

  // キャッシュヒット時は即時全文返却
  if (cacheKey && !body.bypassCache) {
    const cached = getCacheEntry(cacheKey)
    if (cached) {
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(cached)}\n\n`))
          controller.enqueue(encoder.encode('data: [DONE]\n\n'))
          controller.close()
        },
      })
      return sendStream(event, stream)
    }
  }

  const genAI = new GoogleGenerativeAI(config.geminiApiKey)
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.5-flash',
    systemInstruction: 'あなたはプロの料理研究家兼管理栄養士です。',
  })

  // Python版のプロンプトロジックを完全移植
  let prompt = `[使用可能な食材リスト]\n${body.ingredients}\n`

  if (body.useAll) {
    prompt += `
上記の食材リストに記載されているすべての種類の食材を必ずレシピに取り入れてください。
分量はすべてを使い切る必要はなく、少量でも各食材がレシピに登場すればOKです。
食材の数量・重量の目安が記載されている場合は、その量を参考にレシピの分量を調整してください。
`
  } else if (body.isChoi) {
    prompt += `
さらに、一般家庭によくある食材（卵、牛乳、玉ねぎ、各種調味料など）から2〜3品を足して、
より満足度の高いレシピ・献立にしてください。
食材の数量・重量の目安が記載されている場合は、その量に合わせた材料分量でレシピを作成してください。
`
  } else {
    prompt += `
上記の食材の中から適度に選んで、レシピを提案してください。
すべての食材を使い切る必要はありません。
食材の数量・重量の目安が記載されている場合は、その量を参考にレシピの分量調整をしてください。
`
  }

  if (body.easyCooking) {
    prompt += `
[お手軽調理モード]
調理工程をできる限り少なくしてください。「焼いて調味料をかける」「調味料を入れて煮る」「混ぜるだけ」
など、最小限の手順で作れるレシピを優先してください。
調理時間は15分以内を目安に、工程数は3ステップ以内にしてください。
`
  }

  if (body.extraRequest && body.extraRequest.trim()) {
    prompt += `
[ユーザーからの追加要望]
${body.extraRequest.trim()}
上記の追加要望を必ず考慮してレシピを提案してください。
`
  }

  prompt += `
【重要なお願い】
全く異なるアプローチの献立を3パターン（案A, 案B, 案C）提案してください。
各案はそれぞれ【${body.numDishes}品】構成にしてください。
栄養素の概算を考慮し、タンパク質・脂質・炭水化物・野菜のバランスが取れた献立にしてください。

出力フォーマット:
---
## 案A: [コンセプト/料理名]
調理時間: [約〇分]

### [料理名1]
**材料と分量:**
- [食材名]: [具体的な分量（例: 200g、2個、大さじ1）]
- ...
**手順:**
1. ...
**ポイント:** ...

(品数が複数の場合は ### [料理名2] 以降も同様のフォーマットで)

### 栄養素概算
- カロリー: 約〇〇kcal
- タンパク質: 約〇〇g
- 脂質: 約〇〇g
- 炭水化物: 約〇〇g
- 食物繊維: 約〇〇g
---
## 案B: ...
---
## 案C: ...
`

  if (body.mode.includes('離乳食')) {
    const stage = body.mode.replace('離乳食', '').replace(/[()]/g, '')
    prompt += `
【重要】
今回は「${stage}」向けの離乳食レシピです。
1. 食材の大きさ、固さは${stage}の赤ちゃんが安全に食べられるものにしてください。
2. 味付けは月齢に合わせてごく薄味、または素材の味のみにしてください。
3. アレルギー特定原材料が含まれる場合は注意書きをしてください。
4. はちみつ、黒糖、刺身等の危険な食材は絶対に使用しないでください。
5. 必ず冒頭に以下の警告文を表示してください。
「注意：アレルギーや窒息に注意し、初めての食材は少量から試してください。」
`
  } else {
    prompt += `
ターゲット: 忙しい人、家にある食材を使い切りたい人
手軽に作れる家庭料理を提案してください。
`
  }

  try {
    const result = await model.generateContentStream(prompt)

    const stream = new ReadableStream({
      async start(controller) {
        let fullContent = ''
        try {
          for await (const chunk of result.stream) {
            const text = chunk.text()
            if (text) {
              fullContent += text
              controller.enqueue(encoder.encode(`data: ${JSON.stringify(text)}\n\n`))
            }
          }

          // キャッシュ保存（キャッシュ対象かつバイパスでない場合）
          if (cacheKey && !body.bypassCache && fullContent) {
            setCacheEntry(cacheKey, fullContent)
          }

          controller.enqueue(encoder.encode('data: [DONE]\n\n'))
          controller.close()
        } catch (error: any) {
          if (error?.status === 429) {
            controller.enqueue(encoder.encode('data: APIの利用制限に達しました。1分ほど時間を空けてから再度お試しください。\n\n'))
          } else {
            controller.enqueue(encoder.encode(`data: エラーが発生しました: ${error?.message || '不明なエラー'}\n\n`))
          }
          controller.enqueue(encoder.encode('data: [DONE]\n\n'))
          controller.close()
        }
      },
    })

    return sendStream(event, stream)
  } catch (error: any) {
    if (error?.status === 429) {
      return sendStream(event, new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode('data: APIの利用制限に達しました。1分ほど時間を空けてから再度お試しください。\n\n'))
          controller.enqueue(encoder.encode('data: [DONE]\n\n'))
          controller.close()
        },
      }))
    }
    throw createError({ statusCode: 500, statusMessage: error?.message || 'Internal Server Error' })
  }
})
