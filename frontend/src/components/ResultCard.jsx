const CLASS_META = {
  cardboard: { emoji: '📦', bg: 'bg-amber-50',  ring: 'ring-amber-200',  bar: 'bg-amber-400',  text: 'text-amber-700',  label: 'Karton'  },
  glass:     { emoji: '🫙', bg: 'bg-blue-50',   ring: 'ring-blue-200',   bar: 'bg-blue-400',   text: 'text-blue-700',   label: 'Cam'     },
  metal:     { emoji: '🔩', bg: 'bg-slate-50',  ring: 'ring-slate-200',  bar: 'bg-slate-400',  text: 'text-slate-700',  label: 'Metal'   },
  paper:     { emoji: '📄', bg: 'bg-yellow-50', ring: 'ring-yellow-200', bar: 'bg-yellow-400', text: 'text-yellow-700', label: 'Kağıt'   },
  plastic:   { emoji: '🧴', bg: 'bg-cyan-50',   ring: 'ring-cyan-200',   bar: 'bg-cyan-400',   text: 'text-cyan-700',   label: 'Plastik' },
  trash:     { emoji: '🗑️', bg: 'bg-red-50',    ring: 'ring-red-200',    bar: 'bg-red-400',    text: 'text-red-700',    label: 'Çöp'     },
}

export default function ResultCard({ result }) {
  const meta = CLASS_META[result.class_name] ?? {
    emoji: '❓', bg: 'bg-gray-50', ring: 'ring-gray-200',
    bar: 'bg-gray-400', text: 'text-gray-700', label: result.class_name_tr
  }
  const pct = Math.round(result.confidence * 100)

  const sorted = Object.entries(result.probabilities).sort(([, a], [, b]) => b - a)

  return (
    <div className="bg-white rounded-3xl shadow-sm ring-1 ring-gray-100 overflow-hidden">

      {/* Üst banner */}
      <div className={`${meta.bg} ${meta.ring} ring-1 px-6 py-5 flex items-center gap-5`}>
        <div className={`w-16 h-16 rounded-2xl ${meta.bg} ring-2 ${meta.ring} flex items-center justify-center text-3xl flex-shrink-0`}>
          {meta.emoji}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-widest mb-0.5">
            Tespit Edildi
          </p>
          <h2 className={`text-2xl font-bold ${meta.text} truncate`}>{meta.label}</h2>
        </div>
        <div className="text-right flex-shrink-0">
          <div className={`text-4xl font-black ${meta.text}`}>{pct}%</div>
          <p className="text-xs text-gray-400 mt-0.5">güven</p>
        </div>
      </div>

      {/* Güven bar */}
      <div className="px-6 pt-4">
        <div className="w-full bg-gray-100 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${meta.bar} transition-all duration-700`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Tüm sınıflar */}
      <div className="px-6 py-5">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">
          Tüm Sınıflar
        </p>
        <div className="space-y-3">
          {sorted.map(([cls, prob]) => {
            const m = CLASS_META[cls]
            const p = Math.round(prob * 100)
            const isTop = cls === result.class_name
            return (
              <div key={cls} className="flex items-center gap-3">
                <span className="text-xl w-8 text-center flex-shrink-0">{m?.emoji}</span>
                <span className={`w-16 text-sm flex-shrink-0 ${isTop ? 'font-semibold text-gray-800' : 'text-gray-400'}`}>
                  {m?.label}
                </span>
                <div className="flex-1 bg-gray-100 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full transition-all duration-500 ${isTop ? m?.bar : 'bg-gray-200'}`}
                    style={{ width: `${p}%` }}
                  />
                </div>
                <span className={`text-xs w-8 text-right flex-shrink-0 ${isTop ? 'font-semibold text-gray-700' : 'text-gray-300'}`}>
                  {p}%
                </span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 pb-4 flex items-center justify-between">
        <p className="text-xs text-gray-300">EfficientNetV2</p>
        <p className="text-xs text-gray-300">{result.inference_ms} ms</p>
      </div>

    </div>
  )
}
