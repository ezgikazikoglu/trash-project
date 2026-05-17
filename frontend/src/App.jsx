import { useState, useCallback } from 'react'
import UploadZone from './components/UploadZone'
import ResultCard from './components/ResultCard'
import Header from './components/Header'
import './index.css'

export default function App() {
  const [result, setResult] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleFile = useCallback(async (file) => {
    setError(null)
    setResult(null)
    setPreview(URL.createObjectURL(file))
    setLoading(true)

    try {
      const form = new FormData()
      form.append('file', file)
      const base = window.location.protocol === 'file:' ? 'http://localhost:8000' : ''
      const res = await fetch(`${base}/predict`, { method: 'POST', body: form })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Sunucu hatası')
      }
      setResult(await res.json())
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  const handleReset = () => {
    setResult(null)
    setPreview(null)
    setError(null)
  }

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/40 flex items-start justify-center">
      <div className="w-full max-w-xl px-5 py-12">
        <Header />

        {!preview ? (
          <UploadZone onFile={handleFile} />
        ) : (
          <div className="space-y-4">
            {/* Görsel önizleme */}
            <div className="relative rounded-3xl overflow-hidden shadow-sm ring-1 ring-gray-100 bg-white">
              <img
                src={preview}
                alt="Yüklenen görsel"
                className="w-full max-h-72 object-contain"
              />
              {loading && (
                <div className="absolute inset-0 bg-white/70 backdrop-blur-sm flex flex-col items-center justify-center gap-3">
                  <div className="w-10 h-10 border-3 border-emerald-500 border-t-transparent rounded-full animate-spin" />
                  <p className="text-sm font-medium text-emerald-700">Analiz ediliyor...</p>
                </div>
              )}
            </div>

            {error && (
              <div className="bg-red-50 ring-1 ring-red-200 text-red-600 rounded-2xl px-4 py-3 text-sm">
                ⚠️ {error}
              </div>
            )}

            {result && <ResultCard result={result} />}

            <button
              onClick={handleReset}
              className="w-full py-3.5 rounded-2xl border-2 border-emerald-200 text-emerald-700 font-semibold text-sm hover:bg-emerald-50 hover:border-emerald-400 transition-all duration-150"
            >
              ← Yeni Görsel Yükle
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
