import { useCallback, useState } from 'react'

const ACCEPTED = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']

export default function UploadZone({ onFile }) {
  const [dragging, setDragging] = useState(false)

  const process = (file) => {
    if (!file || !ACCEPTED.includes(file.type)) return
    onFile(file)
  }

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    process(e.dataTransfer.files[0])
  }, [])

  const onDragOver = (e) => { e.preventDefault(); setDragging(true) }
  const onDragLeave = () => setDragging(false)
  const onInputChange = (e) => process(e.target.files[0])

  return (
    <label
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      className={`
        group flex flex-col items-center justify-center gap-5
        w-full h-72 rounded-3xl border-2 border-dashed cursor-pointer
        transition-all duration-200
        ${dragging
          ? 'border-emerald-500 bg-emerald-50 scale-[1.01]'
          : 'border-gray-200 bg-white hover:border-emerald-400 hover:bg-emerald-50/40'}
      `}
    >
      <input
        type="file"
        accept={ACCEPTED.join(',')}
        className="hidden"
        onChange={onInputChange}
      />

      <div className={`
        w-20 h-20 rounded-2xl flex items-center justify-center text-4xl
        transition-all duration-200
        ${dragging ? 'bg-emerald-100 scale-110' : 'bg-gray-50 group-hover:bg-emerald-100'}
      `}>
        {dragging ? '📂' : '🖼️'}
      </div>

      <div className="text-center">
        <p className="text-lg font-semibold text-gray-700">
          {dragging ? 'Bırak!' : 'Görsel yükle'}
        </p>
        <p className="text-sm text-gray-400 mt-1">
          Sürükle & bırak <span className="text-gray-300 mx-1">·</span> ya da tıkla seç
        </p>
        <p className="text-xs text-gray-300 mt-3">JPG · PNG · WEBP · maks 10MB</p>
      </div>
    </label>
  )
}
