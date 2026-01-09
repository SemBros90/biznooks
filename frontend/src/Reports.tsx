import React, { useState } from 'react'

export default function Reports(){
  const [start, setStart] = useState('2026-01-01')
  const [end, setEnd] = useState('2026-01-31')
  const [report, setReport] = useState<any>(null)

  const fetchReport = async ()=>{
    const res = await fetch(`/reports/gstr1?start=${start}&end=${end}`)
    const data = await res.json()
    setReport(data)
  }

  return (
    <div>
      <h2>GSTR-1 Summary</h2>
      <div>
        <label>Start <input value={start} onChange={e=>setStart(e.target.value)} /></label>
        <label>End <input value={end} onChange={e=>setEnd(e.target.value)} /></label>
        <button onClick={fetchReport}>Fetch</button>
      </div>
      {report && (
        <pre>{JSON.stringify(report, null, 2)}</pre>
      )}
    </div>
  )
}
