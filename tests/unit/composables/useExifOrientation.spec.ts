import { describe, it, expect, vi } from 'vitest'
import {
  getExifOrientation,
  applyExifOrientation,
} from '../../../app/composables/useExifOrientation'

// JPEG SOI マーカー付きの最小バイト列を生成するヘルパー
function createJpegBuffer(extraBytes: number[] = []): ArrayBuffer {
  const bytes = [0xff, 0xd8, ...extraBytes]
  const buffer = new ArrayBuffer(bytes.length)
  const view = new Uint8Array(buffer)
  bytes.forEach((b, i) => (view[i] = b))
  return buffer
}

function createMockFile(buffer: ArrayBuffer, type = 'image/jpeg'): File {
  const blob = new Blob([buffer], { type })
  return new File([blob], 'test.jpg', { type })
}

describe('getExifOrientation', () => {
  it('JPEG でないファイルは 1 を返す', async () => {
    const buffer = new ArrayBuffer(4)
    const view = new Uint8Array(buffer)
    view[0] = 0x89 // PNG シグネチャ
    view[1] = 0x50
    const file = createMockFile(buffer, 'image/png')
    const result = await getExifOrientation(file)
    expect(result).toBe(1)
  })

  it('EXIF のない JPEG は 1 を返す', async () => {
    const buffer = createJpegBuffer()
    const file = createMockFile(buffer)
    const result = await getExifOrientation(file)
    expect(result).toBe(1)
  })

  it('File の slice と arrayBuffer が呼ばれる', async () => {
    const buffer = createJpegBuffer()
    const file = createMockFile(buffer)
    const sliceSpy = vi.spyOn(file, 'slice')
    await getExifOrientation(file)
    expect(sliceSpy).toHaveBeenCalledWith(0, 65536)
  })
})

describe('applyExifOrientation', () => {
  function createMockCtx() {
    return {
      transform: vi.fn(),
    } as unknown as CanvasRenderingContext2D
  }

  it('orientation 1 (normal) は変換を適用せず [width, height] を返す', () => {
    const ctx = createMockCtx()
    const result = applyExifOrientation(ctx, 1, 100, 200)
    expect(ctx.transform).not.toHaveBeenCalled()
    expect(result).toEqual([100, 200])
  })

  it('orientation 2 (水平反転) は transform(-1,0,0,1,w,0) を適用する', () => {
    const ctx = createMockCtx()
    const result = applyExifOrientation(ctx, 2, 100, 200)
    expect(ctx.transform).toHaveBeenCalledWith(-1, 0, 0, 1, 100, 0)
    expect(result).toEqual([100, 200])
  })

  it('orientation 3 (180度回転) は transform(-1,0,0,-1,w,h) を適用する', () => {
    const ctx = createMockCtx()
    const result = applyExifOrientation(ctx, 3, 100, 200)
    expect(ctx.transform).toHaveBeenCalledWith(-1, 0, 0, -1, 100, 200)
    expect(result).toEqual([100, 200])
  })

  it('orientation 6 (90度回転) は [height, width] を返す', () => {
    const ctx = createMockCtx()
    const result = applyExifOrientation(ctx, 6, 100, 200)
    expect(result).toEqual([200, 100])
  })

  it('orientation 8 (270度回転) は [height, width] を返す', () => {
    const ctx = createMockCtx()
    const result = applyExifOrientation(ctx, 8, 100, 200)
    expect(result).toEqual([200, 100])
  })

  it('未知の orientation は変換なしで [width, height] を返す', () => {
    const ctx = createMockCtx()
    const result = applyExifOrientation(ctx, 99, 100, 200)
    expect(ctx.transform).not.toHaveBeenCalled()
    expect(result).toEqual([100, 200])
  })
})
