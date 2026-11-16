import { useState } from 'react'
import UploadView from './components/UploadView.jsx'
import ResultView from './components/ResultView.jsx'

// display only: picks the symbol shown next to amounts, no conversion
const CURRENCIES = [
  { code: 'USD', symbol: '$' },
  { code: 'EUR', symbol: '€' },
  { code: 'GBP', symbol: '£' },
  { code: 'INR', symbol: '₹' },
  { code: 'AUD', symbol: 'A$' },
  { code: 'CAD', symbol: 'C$' },
]

export default function App() {
  // null = upload screen, object = result screen
  const [result, setResult] = useState(null)
  const [currency, setCurrency] = useState(CURRENCIES[0])

  return (
    <main className="page">
      <header className="top">
        <div>
          <h1>Royalty Split Calculator</h1>
          <p className="sub">Upload a statement, see what each writer is owed.</p>
        </div>
        <label className="currency">
          <span>Statement currency</span>
          <select
            value={currency.code}
            onChange={(e) => setCurrency(CURRENCIES.find((c) => c.code === e.target.value))}
          >
            {CURRENCIES.map((c) => (
              <option key={c.code} value={c.code}>{c.code} ({c.symbol})</option>
            ))}
          </select>
        </label>
      </header>

      {result ? (
        <ResultView result={result} symbol={currency.symbol} onReset={() => setResult(null)} />
      ) : (
        <UploadView onDone={setResult} />
      )}
    </main>
  )
}
