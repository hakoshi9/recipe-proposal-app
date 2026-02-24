import { createHash } from 'crypto'

const MAX_ENTRIES = 100
const TTL_MS = 24 * 60 * 60 * 1000 // 24 hours

interface CacheEntry {
  content: string
  createdAt: number
}

// Module-level LRU cache using Map (insertion order = LRU order)
// Note: In multi-instance environments (e.g. Cloud Run), each instance has its own cache.
// For production with multiple instances, switch to a shared store (e.g. Redis via Upstash).
// To do so, replace this Map with a Nitro Storage driver:
//   useStorage('recipe-cache') with nitro.storage configured in nuxt.config.ts
const cache = new Map<string, CacheEntry>()

export interface CacheKeyParams {
  ingredients: string
  mode: string
  numDishes: number
  isChoi: boolean
  useAll: boolean
  easyCooking: boolean
}

export function buildCacheKey(params: CacheKeyParams): string {
  const sortedIngredients = params.ingredients
    .split('\n')
    .map(s => s.trim())
    .filter(Boolean)
    .sort()
    .join('\n')

  const payload = JSON.stringify({
    ingredients: sortedIngredients,
    mode: params.mode,
    numDishes: params.numDishes,
    isChoi: params.isChoi,
    useAll: params.useAll,
    easyCooking: params.easyCooking,
  })

  return createHash('sha256').update(payload).digest('hex')
}

export function getCacheEntry(key: string): string | null {
  const entry = cache.get(key)
  if (!entry) return null

  if (Date.now() - entry.createdAt > TTL_MS) {
    cache.delete(key)
    return null
  }

  // Move to end to mark as most recently used
  cache.delete(key)
  cache.set(key, entry)

  return entry.content
}

export function setCacheEntry(key: string, content: string): void {
  // Evict expired entries
  const now = Date.now()
  for (const [k, v] of cache.entries()) {
    if (now - v.createdAt > TTL_MS) cache.delete(k)
  }

  // LRU eviction: remove oldest entry when at capacity
  while (cache.size >= MAX_ENTRIES) {
    const oldestKey = cache.keys().next().value!
    cache.delete(oldestKey)
  }

  cache.set(key, { content, createdAt: now })
}
