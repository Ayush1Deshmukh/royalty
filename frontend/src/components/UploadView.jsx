import { useRef, useState } from 'react'
import { uploadStatement } from '../api.js'

export default function UploadView({ onDone }) {
  const [file, setFile] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  function clearFile() {
    setFile(null)
    if (inputRef.current) inputRef.current.value = '' // so same file can be picked again
  }

  function pick(picked) {
    if (!picked) return
    // accept attr doesn't cover drag-drop, so check here too
    if (!picked.name.toLowerCase().endsWith('.csv')) {
      clearFile()
      setError(`"${picked.name}" is not a .csv file. Export the statement as CSV and try again.`)
      return
    }
    setError('')
    setFile(picked)
  }

  function onDrop(e) {
    e.preventDefault()
    setDragging(false)
    if (!loading) pick(e.dataTransfer.files[0])
  }

  async function upload() {
    setLoading(true)
    setError('')
    try {
      onDone(await uploadStatement(file))
    } catch (err) {
      // file rejected -> show server msg, stay here, clear selection
      setError(err.message)
      clearFile()
      setLoading(false)
    }
  }

  return (
    <section className="panel upload reveal">
      <label
        className={`dropzone${dragging ? ' dragging' : ''}${file ? ' has-file' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          disabled={loading}
          onChange={(e) => pick(e.target.files[0])}
        />
        <svg className="drop-icon" viewBox="0 0 24 24" aria-hidden="true">
          {file ? (
            <path d="M7 3h7l5 5v13H7z M14 3v5h5 M10 13h6 M10 17h6" />
          ) : (
            <path d="M12 16V5 M7.5 9.5 12 5l4.5 4.5 M5 19h14" />
          )}
        </svg>
        {file ? (
          <>
            <strong className="filename">{file.name}</strong>
            <small>Click to choose a different file</small>
          </>
        ) : (
          <>
            <span>Drop a royalty statement here, or <u>choose a file</u></span>
            <small>.csv only, up to 5 MB</small>
          </>
        )}
      </label>

      <p className="hint">
        The file needs the columns <code>work_id</code>, <code>title</code>, <code>amount</code>.{' '}
        <a href="/sample-statement.csv" download>Download a sample CSV</a>
      </p>

      {/* key restarts the animation when the message changes */}
      {error && <p className="alert" role="alert" key={error}>{error}</p>}

      <button className="btn primary" onClick={upload} disabled={!file || loading}>
        {loading && <span className="spinner" aria-hidden="true" />}
        {loading ? 'Uploading…' : 'Upload'}
      </button>
    </section>
  )
}
