// all backend calls live here

const BASE = '/api/statements'

async function readError(res) {
  // backend sends { detail: "..." } on errors
  try {
    const body = await res.json()
    if (typeof body.detail === 'string') return body.detail
  } catch {
    // not json, fall through
  }
  return `Upload failed (status ${res.status}). Check the backend is running and try again.`
}

// POST the csv, then GET the full result (summary + lines)
export async function uploadStatement(file) {
  const form = new FormData()
  form.append('file', file)

  let res
  try {
    res = await fetch(BASE, { method: 'POST', body: form })
  } catch {
    throw new Error('Could not reach the server. Start the backend and try again.')
  }
  if (!res.ok) throw new Error(await readError(res))
  const { id } = await res.json()

  const detail = await fetch(`${BASE}/${id}`)
  if (!detail.ok) throw new Error(await readError(detail))
  return detail.json()
}

export function sharesCsvUrl(id) {
  return `${BASE}/${id}/shares.csv`
}
