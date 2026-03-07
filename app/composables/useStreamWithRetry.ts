interface StreamRetryOptions {
  maxRetries?: number
  baseDelayMs?: number
  onChunk: (chunk: string) => void
  onRetry?: (attempt: number, delayMs: number, reason: string) => void
  onError?: (message: string) => void
}

interface StreamRetryState {
  isRetrying: Ref<boolean>
  retryCountdown: Ref<number>
  retryAttempt: Ref<number>
}

export function useStreamWithRetry(): StreamRetryState & {
  fetchStream: (url: string, options: RequestInit, retryOptions: StreamRetryOptions) => Promise<void>
  cancel: () => void
} {
  const isRetrying = ref(false)
  const retryCountdown = ref(0)
  const retryAttempt = ref(0)

  let cancelled = false
  let countdownTimer: ReturnType<typeof setInterval> | null = null

  const clearCountdown = () => {
    if (countdownTimer) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }

  const cancel = () => {
    cancelled = true
    clearCountdown()
    isRetrying.value = false
    retryCountdown.value = 0
    retryAttempt.value = 0
  }

  const wait = (ms: number, attempt: number, reason: string, onRetry?: StreamRetryOptions['onRetry']): Promise<void> => {
    return new Promise((resolve) => {
      const seconds = Math.ceil(ms / 1000)
      isRetrying.value = true
      retryCountdown.value = seconds
      onRetry?.(attempt, ms, reason)

      countdownTimer = setInterval(() => {
        if (cancelled) {
          clearCountdown()
          resolve()
          return
        }
        retryCountdown.value -= 1
        if (retryCountdown.value <= 0) {
          clearCountdown()
          isRetrying.value = false
          resolve()
        }
      }, 1000)
    })
  }

  const fetchStream = async (
    url: string,
    fetchOptions: RequestInit,
    { maxRetries = 3, baseDelayMs = 1000, onChunk, onRetry, onError }: StreamRetryOptions,
  ): Promise<void> => {
    cancelled = false
    retryAttempt.value = 0

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      if (cancelled) return

      try {
        const response = await fetch(url, fetchOptions)

        if (!response.ok) {
          if (response.status === 429 && attempt < maxRetries) {
            const retryAfter = response.headers.get('Retry-After')
            const delayMs = retryAfter ? parseInt(retryAfter) * 1000 : baseDelayMs * Math.pow(2, attempt)
            retryAttempt.value = attempt + 1
            await wait(delayMs, attempt + 1, 'rate_limit', onRetry)
            continue
          }
          throw Object.assign(new Error(`HTTP ${response.status}`), { status: response.status })
        }

        const reader = response.body?.getReader()
        const decoder = new TextDecoder()
        if (!reader) throw new Error('No readable stream')

        let buffer = ''
        let streamError: { type: string; message: string } | null = null

        while (true) {
          if (cancelled) {
            reader.cancel()
            return
          }

          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('event: error')) {
              // next line will be data: {...}
              continue
            }
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              if (data === '[DONE]') break

              // Check for structured error data
              try {
                const parsed = JSON.parse(data)
                if (parsed && typeof parsed === 'object' && parsed.__error) {
                  streamError = parsed
                  continue
                }
                // Regular string chunk
                onChunk(parsed)
              } catch {
                // Not JSON, treat as plain text chunk
                onChunk(data)
              }
            }
          }

          if (streamError) break
        }

        if (streamError) {
          if (streamError.type === 'rate_limit' && attempt < maxRetries) {
            const delayMs = baseDelayMs * Math.pow(2, attempt)
            retryAttempt.value = attempt + 1
            await wait(delayMs, attempt + 1, 'rate_limit', onRetry)
            continue
          }
          onError?.(streamError.message || 'ストリームエラーが発生しました')
          return
        }

        // Success
        isRetrying.value = false
        retryAttempt.value = 0
        return
      } catch (err) {
        if (cancelled) return

        const isNetworkError = err instanceof TypeError
        if (isNetworkError && attempt < maxRetries) {
          const delayMs = baseDelayMs * Math.pow(2, attempt)
          retryAttempt.value = attempt + 1
          await wait(delayMs, attempt + 1, 'network', onRetry)
          continue
        }

        throw err
      }
    }
  }

  return { isRetrying, retryCountdown, retryAttempt, fetchStream, cancel }
}
