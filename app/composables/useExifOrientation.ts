/**
 * JPEG EXIF Orientation タグ (0x0112) を読み取るユーティリティ。
 * 外部ライブラリ不使用。orientation 値 (1〜8) を返す。
 * JPEG でない場合や EXIF が存在しない場合は 1 (normal) を返す。
 */
export async function getExifOrientation(file: File): Promise<number> {
  const buffer = await file.slice(0, 65536).arrayBuffer()
  const view = new DataView(buffer)

  // JPEG SOI マーカーチェック
  if (view.getUint16(0) !== 0xffd8) return 1

  let offset = 2
  while (offset < view.byteLength - 2) {
    const marker = view.getUint16(offset)
    offset += 2

    // APP1 マーカー (0xFFE1) = Exif が含まれる可能性あり
    if (marker === 0xffe1) {
      const segmentLength = view.getUint16(offset)
      // "Exif\0\0" の確認
      if (
        view.getUint32(offset + 2) === 0x45786966 &&
        view.getUint16(offset + 6) === 0x0000
      ) {
        const tiffStart = offset + 8
        const byteOrder = view.getUint16(tiffStart)
        const littleEndian = byteOrder === 0x4949

        const readUint16 = (o: number) =>
          view.getUint16(tiffStart + o, littleEndian)
        const readUint32 = (o: number) =>
          view.getUint32(tiffStart + o, littleEndian)

        // TIFF ヘッダー確認 (0x002A)
        if (readUint16(2) !== 0x002a) return 1

        const ifdOffset = readUint32(4)
        const entryCount = readUint16(ifdOffset)

        for (let i = 0; i < entryCount; i++) {
          const entryOffset = ifdOffset + 2 + i * 12
          const tag = readUint16(entryOffset)
          if (tag === 0x0112) {
            // Orientation タグ
            return readUint16(entryOffset + 8)
          }
        }
      }
      offset += segmentLength
    } else if ((marker & 0xff00) === 0xff00) {
      // 他のマーカーはスキップ
      offset += view.getUint16(offset)
    } else {
      break
    }
  }

  return 1
}

/**
 * EXIF Orientation 値に基づき、canvas に変換行列を適用する。
 * 呼び出し前に canvas のサイズを正しい出力サイズ（回転後）に設定すること。
 *
 * @returns [outputWidth, outputHeight] — 回転後の正しいキャンバスサイズ
 */
export function applyExifOrientation(
  ctx: CanvasRenderingContext2D,
  orientation: number,
  width: number,
  height: number,
): [number, number] {
  switch (orientation) {
    case 2:
      ctx.transform(-1, 0, 0, 1, width, 0)
      return [width, height]
    case 3:
      ctx.transform(-1, 0, 0, -1, width, height)
      return [width, height]
    case 4:
      ctx.transform(1, 0, 0, -1, 0, height)
      return [width, height]
    case 5:
      ctx.transform(0, 1, 1, 0, 0, 0)
      return [height, width]
    case 6:
      ctx.transform(0, 1, -1, 0, height, 0)
      return [height, width]
    case 7:
      ctx.transform(0, -1, -1, 0, height, width)
      return [height, width]
    case 8:
      ctx.transform(0, -1, 1, 0, 0, width)
      return [height, width]
    default:
      return [width, height]
  }
}
