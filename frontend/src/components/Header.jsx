export default function Header() {
  return (
    <div className="text-center mb-8">
      <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-emerald-100 mb-4">
        <span className="text-4xl">♻️</span>
      </div>
      <h1 className="text-4xl font-bold text-gray-800 mb-2 tracking-tight">
        Atık Sınıflandırıcı
      </h1>
      <p className="text-gray-500 text-base leading-relaxed">
        Görselinizi yükleyin, yapay zeka atık türünü saniyeler içinde tespit etsin
      </p>
    </div>
  )
}
