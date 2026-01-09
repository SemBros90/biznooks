import React, { useEffect, useState } from 'react'

export default function InvoiceList(){
  const [invoices, setInvoices] = useState<any[]>([])

  useEffect(()=>{
    fetch('/invoices')
      .then(r=>r.json())
      .then(data=>{
        // API does not have list endpoint in prototype; show demo placeholder
        setInvoices([])
      })
      .catch(()=>setInvoices([]))
  },[])

  return (
    <div>
      <h2>Invoices</h2>
      <p>This prototype does not expose a list API — use demo scripts or the POST /invoices endpoint.</p>
      <ul>
        {invoices.map(inv=> <li key={inv.id}>{inv.invoice_number}</li>)}
      </ul>
    </div>
  )
}
