import { GoogleGenerativeAI } from '@google/generative-ai'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const { images } = await readBody<{ images: string[] }>(event)

  if (!images || images.length === 0) {
    throw createError({ statusCode: 400, statusMessage: '画像が指定されていません' })
  }

  const genAI = new GoogleGenerativeAI(config.geminiApiKey)
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.5-flash',
    systemInstruction: 'あなたは画像解析のエキスパートです。余計な会話はせず、結果のみを出力します。',
  })

  const prompt = `写っている食材をすべてリストアップしてください。
各食材について、写真から判断できる数量や重さの目安も合わせて出力してください。
数量が不明確な場合は「少々」「数枚程度」など推定で構いません。
出力フォーマット:
- [食材名]: [数量・重量の目安]
例:
- とんかつ: 3個程度
- 魚の切り身: 2切れ程度
- 小松菜: 山盛りになる程度（1束程度）
余計な文章は含めず、箇条書きのリストのみを出力してください。`

  const imageParts = images.map((base64) => ({
    inlineData: {
      data: base64,
      mimeType: 'image/jpeg' as const,
    },
  }))

  setResponseHeader(event, 'Content-Type', 'text/event-stream')
  setResponseHeader(event, 'Cache-Control', 'no-cache')
  setResponseHeader(event, 'Connection', 'keep-alive')

  try {
    const result = await model.generateContentStream({
      contents: [{ role: 'user', parts: [{ text: prompt }, ...imageParts] }],
      generationConfig: {
        maxOutputTokens: 500,
        temperature: 0.0,
      },
    })

    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      async start(controller) {
        try {
          for await (const chunk of result.stream) {
            const text = chunk.text()
            if (text) {
              controller.enqueue(encoder.encode(`data: ${JSON.stringify(text)}\n\n`))
            }
          }
          controller.enqueue(encoder.encode('data: [DONE]\n\n'))
          controller.close()
        } catch (error: any) {
          if (error?.status === 429) {
            controller.enqueue(encoder.encode('data: APIの利用制限（1分間の回数制限）に達しました。1分ほど時間を空けてから、もう一度ボタンを押してください。\n\n'))
          } else {
            controller.enqueue(encoder.encode(`data: エラー: ${error?.message || '不明なエラー'}\n\n`))
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
          const encoder = new TextEncoder()
          controller.enqueue(encoder.encode('data: APIの利用制限に達しました。1分ほど時間を空けてから再度お試しください。\n\n'))
          controller.enqueue(encoder.encode('data: [DONE]\n\n'))
          controller.close()
        },
      }))
    }
    throw createError({ statusCode: 500, statusMessage: error?.message || 'Internal Server Error' })
  }
})
