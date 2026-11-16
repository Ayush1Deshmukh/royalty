import { sharesCsvUrl } from '../api.js'

const UNMATCHED = 'UNMATCHED'

export default function ResultView({ result, symbol, onReset }) {
  const { errors, writerTotals, lineResults, reconciled } = result

  // display only: backend already gives 2-decimal strings, we just add the symbol
  const money = (amount) => `${symbol}${amount}`

  return (
    <div className="reveal">
      <section className="stats">
        <Stat label="File total" value={money(result.fileTotal)} />
        <Stat label="Allocated" value={money(result.allocatedTotal)} />
        <Stat label="Unmatched" value={money(result.unmatchedTotal)} />
        <Stat label="Lines" value={result.lines} />
      </section>

      {/* reconciled flag comes from the backend, no math here */}
      <p className={`recon ${reconciled ? 'ok' : 'bad'}`}>
        <svg className="mark" viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="12" r="10" />
          <path d={reconciled ? 'M7 12.5l3.5 3.5L17 9' : 'M8 8l8 8M16 8l-8 8'} />
        </svg>
        <span>
          <strong>{reconciled ? 'Reconciled' : 'Not reconciled'}.</strong>{' '}
          Allocated {money(result.allocatedTotal)} + unmatched {money(result.unmatchedTotal)}{' '}
          {reconciled ? '=' : '≠'} file total {money(result.fileTotal)}
        </span>
      </p>

      <div className="actions">
        <a className="btn primary" href={sharesCsvUrl(result.id)} download="shares.csv">
          Download shares.csv
        </a>
        <button className="btn" onClick={onReset}>Upload another file</button>
      </div>

      {errors.length > 0 && (
        <section className="panel errors">
          <h2>Row errors <span className="count">{errors.length}</span></h2>
          <p>These rows were skipped. Fix them in the file and upload it again.</p>
          <ul>
            {errors.map((e) => (
              <li key={e.row}><b>Row {e.row}:</b> {e.reason}</li>
            ))}
          </ul>
        </section>
      )}

      <section className="panel">
        <h2>Writer totals</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Writer</th><th className="num">Amount</th></tr>
            </thead>
            <tbody>
              {/* already sorted by the backend, highest first */}
              {writerTotals.map((w) => (
                <tr key={w.writer}>
                  <td>{w.writer}</td>
                  <td className="num">{money(w.amount)}</td>
                </tr>
              ))}
              {writerTotals.length === 0 && (
                <tr><td colSpan="2" className="empty">No writers were paid from this file.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel">
        <h2>Line breakdown</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Work</th><th>Title</th><th>Writer</th>
                <th className="num">Share %</th><th className="num">Amount</th>
              </tr>
            </thead>
            <tbody>
              {lineResults.map((l) => {
                const unmatched = l.writer === UNMATCHED
                return (
                  <tr key={`${l.workId}-${l.writer}`} className={unmatched ? 'unmatched' : ''}>
                    <td className="id">{l.workId}</td>
                    <td>{l.title}</td>
                    <td>{unmatched ? <span className="tag">Unmatched</span> : l.writer}</td>
                    <td className="num">{l.sharePercent}</td>
                    <td className="num">{money(l.amount)}</td>
                  </tr>
                )
              })}
              {lineResults.length === 0 && (
                <tr><td colSpan="5" className="empty">No valid rows in this file.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <span className="label">{label}</span>
      <span className="value">{value}</span>
    </div>
  )
}
