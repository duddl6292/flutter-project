import { DRAG_MODE, Niivue, SLICE_TYPE } from '@niivue/niivue'
import {
  Camera,
  ChevronLeft,
  ChevronRight,
  Columns3,
  Contrast,
  Download,
  Eye,
  EyeOff,
  RotateCcw,
  ScanLine,
  ZoomIn,
  ZoomOut,
} from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

import { downloadCTAsset } from './ct-analysis.api'

interface NiiVueViewerProps {
  sourceUrl: string
  maskUrl: string
  displayId: string
  lesionDetected: boolean
  lesionSliceIndices: number[]
  lesionSliceStart: number | null
  lesionSliceEnd: number | null
  maxLesionSlice: number | null
}

type SliceAxis = 'x' | 'y' | 'z'
type ViewerMode = 'axial' | 'coronal' | 'sagittal' | 'multiplanar' | 'render'

const sliceTypeByMode: Record<ViewerMode, SLICE_TYPE> = {
  axial: SLICE_TYPE.AXIAL,
  coronal: SLICE_TYPE.CORONAL,
  sagittal: SLICE_TYPE.SAGITTAL,
  multiplanar: SLICE_TYPE.MULTIPLANAR,
  render: SLICE_TYPE.RENDER,
}

const sliceAxisByMode: Record<Exclude<ViewerMode, 'render'>, SliceAxis> = {
  axial: 'z',
  coronal: 'y',
  sagittal: 'x',
  multiplanar: 'z',
}

const sliceLabelByAxis: Record<SliceAxis, string> = {
  x: '시상면',
  y: '관상면',
  z: '축상면',
}

function formatSliceRanges(indices: number[]): string {
  const slices = [...new Set(indices.map((index) => index + 1))].sort((a, b) => a - b)
  if (slices.length === 0) return '-'
  const ranges: string[] = []
  let start = slices[0]
  let end = slices[0]
  for (const slice of slices.slice(1)) {
    if (slice === end + 1) {
      end = slice
      continue
    }
    ranges.push(start === end ? `${start}` : `${start}–${end}`)
    start = slice
    end = slice
  }
  ranges.push(start === end ? `${start}` : `${start}–${end}`)
  return ranges.join(', ')
}

function configureMouseControls(niivue: Niivue, mode: ViewerMode): void {
  niivue.setMouseEventConfig({
    leftButton: {
      primary: mode === 'render' ? DRAG_MODE.crosshair : DRAG_MODE.pan,
      withCtrl: DRAG_MODE.crosshair,
      withShift: DRAG_MODE.windowing,
    },
    rightButton: DRAG_MODE.windowing,
    centerButton: DRAG_MODE.pan,
  })
}

export function NiiVueViewer({
  sourceUrl,
  maskUrl,
  displayId,
  lesionDetected,
  lesionSliceIndices = [],
  lesionSliceStart,
  lesionSliceEnd,
  maxLesionSlice,
}: NiiVueViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const niivueRef = useRef<Niivue | null>(null)
  const [opacity, setOpacity] = useState(0.55)
  const [maskVisible, setMaskVisible] = useState(true)
  const [viewerMode, setViewerMode] = useState<ViewerMode>('multiplanar')
  const [zoom, setZoom] = useState(1)
  const [sliceCounts, setSliceCounts] = useState<Record<SliceAxis, number>>({ x: 1, y: 1, z: 1 })
  const [slicePositions, setSlicePositions] = useState<Record<SliceAxis, number>>({ x: 1, y: 1, z: 1 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let disposed = false
    const objectUrls: string[] = []
    let attachedCanvas: HTMLCanvasElement | null = null
    let wheelHandler: ((event: WheelEvent) => void) | null = null
    const load = async () => {
      if (!canvasRef.current) return
      setLoading(true)
      setError('')
      try {
        const [source, mask] = await Promise.all([
          downloadCTAsset(sourceUrl),
          downloadCTAsset(maskUrl),
        ])
        if (disposed) return
        const sourceObjectUrl = URL.createObjectURL(source)
        const maskObjectUrl = URL.createObjectURL(mask)
        objectUrls.push(sourceObjectUrl, maskObjectUrl)
        const niivue = new Niivue({
          backColor: [0.025, 0.035, 0.07, 1],
          crosshairColor: [0.45, 0.9, 1, 1],
          sliceType: SLICE_TYPE.MULTIPLANAR,
          isColorbar: true,
          dragAndDropEnabled: false,
        })
        configureMouseControls(niivue, 'multiplanar')
        niivue.onLocationChange = (location) => {
          const vox = (location as { vox?: number[] }).vox
          if (!vox || vox.length < 3) return
          setSlicePositions({
            x: Math.round(vox[0]) + 1,
            y: Math.round(vox[1]) + 1,
            z: Math.round(vox[2]) + 1,
          })
        }
        niivueRef.current = niivue
        await niivue.attachToCanvas(canvasRef.current)
        await niivue.loadVolumes([
          {
            url: sourceObjectUrl,
            name: `${displayId}-source.nii.gz`,
            colormap: 'gray',
            opacity: 1,
          },
          {
            url: maskObjectUrl,
            name: `${displayId}-mask.nii.gz`,
            colormap: 'red',
            opacity,
            cal_min: 0.5,
            cal_max: 1,
            trustCalMinMax: true,
            alphaThreshold: true,
          },
        ])
        const dimensions = niivue.volumes[0]?.dimsRAS
        if (dimensions && dimensions.length >= 4) {
          const counts = {
            x: Math.max(1, Math.round(dimensions[1])),
            y: Math.max(1, Math.round(dimensions[2])),
            z: Math.max(1, Math.round(dimensions[3])),
          }
          setSliceCounts(counts)
          setSlicePositions({
            x: Math.round((counts.x + 1) / 2),
            y: Math.round((counts.y + 1) / 2),
            z: Math.round((counts.z + 1) / 2),
          })
        }
        attachedCanvas = canvasRef.current
        wheelHandler = (event) => {
          if (!attachedCanvas || disposed || event.deltaY === 0) return
          event.preventDefault()
          event.stopImmediatePropagation()

          const isRender = niivue.opts.sliceType === SLICE_TYPE.RENDER
          const currentZoom = isRender
            ? niivue.scene.volScaleMultiplier
            : niivue.scene.pan2Dxyzmm[3]
          const zoomFactor = event.deltaY < 0 ? 1.1 : 1 / 1.1
          const nextZoom = Math.min(4, Math.max(0.5, currentZoom * zoomFactor))

          if (isRender) {
            niivue.setScale(nextZoom)
          } else {
            const rect = attachedCanvas.getBoundingClientRect()
            const canvasX = (event.clientX - rect.left) * (attachedCanvas.width / rect.width)
            const canvasY = (event.clientY - rect.top) * (attachedCanvas.height / rect.height)
            const focus = niivue.canvasPos2frac([canvasX, canvasY])
            if (focus[0] >= 0 && focus[1] >= 0 && focus[2] >= 0) {
              niivue.scene.crosshairPos = focus
              const vox = niivue.frac2vox(focus)
              setSlicePositions({
                x: Math.round(vox[0]) + 1,
                y: Math.round(vox[1]) + 1,
                z: Math.round(vox[2]) + 1,
              })
              const focusMM = niivue.frac2mm(focus)
              const zoomChange = currentZoom - nextZoom
              const [panX, panY, panZ] = niivue.scene.pan2Dxyzmm
              niivue.setPan2Dxyzmm([
                panX + zoomChange * focusMM[0],
                panY + zoomChange * focusMM[1],
                panZ + zoomChange * focusMM[2],
                nextZoom,
              ])
            } else {
              const [panX, panY, panZ] = niivue.scene.pan2Dxyzmm
              niivue.setPan2Dxyzmm([panX, panY, panZ, nextZoom])
            }
          }
          setZoom(nextZoom)
        }
        attachedCanvas.addEventListener('wheel', wheelHandler, { capture: true, passive: false })
      } catch (loadError) {
        if (!disposed) {
          setError(loadError instanceof Error ? loadError.message : 'CT 영상을 표시하지 못했습니다.')
        }
      } finally {
        if (!disposed) setLoading(false)
      }
    }
    void load()
    return () => {
      disposed = true
      if (attachedCanvas && wheelHandler) {
        attachedCanvas.removeEventListener('wheel', wheelHandler, true)
      }
      niivueRef.current?.cleanup()
      niivueRef.current = null
      objectUrls.forEach((url) => URL.revokeObjectURL(url))
    }
  }, [displayId, maskUrl, sourceUrl])

  useEffect(() => {
    niivueRef.current?.setOpacity(1, maskVisible ? opacity : 0)
  }, [maskVisible, opacity])

  const changeViewerMode = (mode: ViewerMode) => {
    setViewerMode(mode)
    const niivue = niivueRef.current
    if (!niivue) return
    niivue.setSliceType(sliceTypeByMode[mode])
    configureMouseControls(niivue, mode)
  }

  const activeSliceAxis = viewerMode === 'render' ? null : sliceAxisByMode[viewerMode]
  const activeSlice = activeSliceAxis ? slicePositions[activeSliceAxis] : 1
  const activeSliceCount = activeSliceAxis ? sliceCounts[activeSliceAxis] : 1

  const changeSlice = (requestedSlice: number) => {
    const niivue = niivueRef.current
    if (!niivue || !activeSliceAxis) return
    const nextSlice = Math.min(activeSliceCount, Math.max(1, requestedSlice))
    const distance = nextSlice - activeSlice
    if (distance === 0) return
    if (activeSliceAxis === 'x') niivue.moveCrosshairInVox(distance, 0, 0)
    if (activeSliceAxis === 'y') niivue.moveCrosshairInVox(0, distance, 0)
    if (activeSliceAxis === 'z') niivue.moveCrosshairInVox(0, 0, distance)
    setSlicePositions((current) => ({ ...current, [activeSliceAxis]: nextSlice }))
  }

  const changeZoom = (amount: number) => {
    const nextZoom = Math.min(4, Math.max(0.5, Number((zoom + amount).toFixed(2))))
    const niivue = niivueRef.current
    if (viewerMode === 'render') {
      niivue?.setScale(nextZoom)
    } else if (niivue) {
      const [panX, panY, panZ, currentZoom] = niivue.scene.pan2Dxyzmm
      const focusMM = niivue.frac2mm(niivue.scene.crosshairPos)
      const zoomChange = currentZoom - nextZoom
      niivue.setPan2Dxyzmm([
        panX + zoomChange * focusMM[0],
        panY + zoomChange * focusMM[1],
        panZ + zoomChange * focusMM[2],
        nextZoom,
      ])
    }
    setZoom(nextZoom)
  }

  const resetView = () => {
    const niivue = niivueRef.current
    if (!niivue) return
    const center = {
      x: Math.round((sliceCounts.x + 1) / 2),
      y: Math.round((sliceCounts.y + 1) / 2),
      z: Math.round((sliceCounts.z + 1) / 2),
    }
    niivue.moveCrosshairInVox(
      center.x - slicePositions.x,
      center.y - slicePositions.y,
      center.z - slicePositions.z,
    )
    niivue.setPan2Dxyzmm([0, 0, 0, 1])
    niivue.setScale(1)
    setSlicePositions(center)
    setZoom(1)
  }

  const resetContrast = () => {
    const niivue = niivueRef.current
    const sourceVolume = niivue?.volumes[0]
    if (!niivue || !sourceVolume) return
    sourceVolume.cal_min = sourceVolume.robust_min
    sourceVolume.cal_max = sourceVolume.robust_max
    niivue.refreshLayers(sourceVolume, 0)
    niivue.drawScene()
  }

  const goToLargestLesionSlice = () => {
    if (maxLesionSlice === null) return
    if (viewerMode !== 'axial') changeViewerMode('axial')
    const currentZ = slicePositions.z
    const targetZ = Math.min(sliceCounts.z, Math.max(1, maxLesionSlice + 1))
    niivueRef.current?.moveCrosshairInVox(0, 0, targetZ - currentZ)
    setSlicePositions((current) => ({ ...current, z: targetZ }))
  }

  const savePng = () => {
    canvasRef.current?.toBlob((blob) => {
      if (!blob) return
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = `${displayId}-overlay.png`
      anchor.click()
      URL.revokeObjectURL(url)
    }, 'image/png')
  }

  return (
    <section className="ct-viewer-card">
      <header>
        <div><ScanLine size={20} /><div><h2>원본 CT + AI 마스크</h2><p>빨간 영역이 AI가 분할한 병변 마스크입니다.</p></div></div>
        <div className="ct-viewer-actions">
          <button type="button" className={viewerMode === 'multiplanar' ? 'active' : ''} onClick={() => changeViewerMode('multiplanar')}><Columns3 size={16} /> 다중</button>
          <button type="button" className={viewerMode === 'render' ? 'active' : ''} onClick={() => changeViewerMode('render')}><Camera size={16} /> 3D</button>
          <button type="button" onClick={savePng} disabled={loading}><Download size={16} /> 오버레이 PNG 저장</button>
        </div>
      </header>
      {lesionDetected && lesionSliceStart !== null && lesionSliceEnd !== null && (
        <div className="ct-lesion-slice-summary">
          <span>병변이 있는 슬라이스 <strong>{lesionSliceIndices.length > 0 ? formatSliceRanges(lesionSliceIndices) : `${lesionSliceStart + 1}–${lesionSliceEnd + 1}`}번</strong></span>
          {maxLesionSlice !== null && <span>가장 큰 병변 <strong>{maxLesionSlice + 1}번 슬라이스</strong></span>}
          {maxLesionSlice !== null && <button type="button" onClick={goToLargestLesionSlice}>최대 병변 위치로 이동</button>}
        </div>
      )}
      {!lesionDetected && <div className="ct-lesion-slice-summary normal"><span>분석된 슬라이스에서 병변이 탐지되지 않았습니다.</span></div>}
      <div className="ct-viewer-toolbar">
        <div className="ct-view-mode-group" aria-label="단면 선택">
          <button type="button" className={viewerMode === 'axial' ? 'active' : ''} onClick={() => changeViewerMode('axial')}>축상면</button>
          <button type="button" className={viewerMode === 'coronal' ? 'active' : ''} onClick={() => changeViewerMode('coronal')}>관상면</button>
          <button type="button" className={viewerMode === 'sagittal' ? 'active' : ''} onClick={() => changeViewerMode('sagittal')}>시상면</button>
        </div>
        <div className="ct-viewer-tool-group">
          <button type="button" onClick={() => setMaskVisible((visible) => !visible)} aria-pressed={maskVisible}>
            {maskVisible ? <EyeOff size={15} /> : <Eye size={15} />}
            {maskVisible ? '마스크 숨기기' : '마스크 표시'}
          </button>
          <button type="button" onClick={() => changeZoom(-0.25)} disabled={loading || zoom <= 0.5} aria-label="축소"><ZoomOut size={16} /></button>
          <span className="ct-zoom-value">{Math.round(zoom * 100)}%</span>
          <button type="button" onClick={() => changeZoom(0.25)} disabled={loading || zoom >= 4} aria-label="확대"><ZoomIn size={16} /></button>
          <button type="button" onClick={resetContrast} disabled={loading}><Contrast size={15} /> 명암 초기화</button>
          <button type="button" onClick={resetView} disabled={loading}><RotateCcw size={15} /> 화면 맞춤</button>
        </div>
      </div>
      <div className="ct-opacity-control">
        <label htmlFor="mask-opacity">마스크 투명도</label>
        <input id="mask-opacity" type="range" min="0" max="1" step="0.05" value={opacity} disabled={!maskVisible} onChange={(event) => setOpacity(Number(event.target.value))} />
        <span>{maskVisible ? `${Math.round(opacity * 100)}%` : '숨김'}</span>
      </div>
      <div className="ct-slice-control">
        <button type="button" onClick={() => changeSlice(activeSlice - 1)} disabled={loading || !activeSliceAxis || activeSlice <= 1} aria-label="이전 슬라이스"><ChevronLeft size={17} /></button>
        <label htmlFor="ct-slice-range">{activeSliceAxis ? sliceLabelByAxis[activeSliceAxis] : '3D 렌더링'}</label>
        <input id="ct-slice-range" type="range" min="1" max={activeSliceCount} step="1" value={activeSlice} disabled={loading || !activeSliceAxis} onChange={(event) => changeSlice(Number(event.target.value))} />
        <strong>{activeSliceAxis ? `${activeSlice} / ${activeSliceCount}` : '-'}</strong>
        <button type="button" onClick={() => changeSlice(activeSlice + 1)} disabled={loading || !activeSliceAxis || activeSlice >= activeSliceCount} aria-label="다음 슬라이스"><ChevronRight size={17} /></button>
      </div>
      <p className="ct-viewer-hint">좌클릭 드래그: 화면 이동 · 휠: 포인터 중심 확대·축소 · Shift+드래그: 명암 조절 · 더블클릭: 명암 초기화</p>
      <div className="ct-canvas-wrap">
        {loading && <div className="ct-viewer-state">영상을 불러오는 중입니다.</div>}
        {error && <div className="ct-viewer-state error" role="alert">{error}</div>}
        <canvas ref={canvasRef} aria-label="원본 CT와 AI 마스크 오버레이 뷰어" />
      </div>
    </section>
  )
}
