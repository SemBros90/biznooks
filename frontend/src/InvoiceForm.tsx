import React, { useState } from 'react'

export default function InvoiceForm(){
  const [invoiceNumber, setInvoiceNumber] = useState('')
  const [currency, setCurrency] = useState('INR')
  const [customerName, setCustomerName] = useState('')

  const submit = async (e:any)=>{
    e.preventDefault()
    const payload = {
      invoice_number: invoiceNumber,
      date: new Date().toISOString().slice(0,10),
      customer_name: customerName,
      currency: currency,
      lines: [{description:'Item', quantity:1, unit_rate:100, amount:100}]
    }
    const res = await fetch('/invoices', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)})
    const data = await res.json()
    alert('Created invoice id: ' + (data.invoice_id || JSON.stringify(data)))
  }

  return (
    <div>
      <h2>Create Invoice</h2>
      <form onSubmit={submit}>
        <div>
          <label>Invoice No: <input value={invoiceNumber} onChange={e=>setInvoiceNumber(e.target.value)} /></label>
        </div>
        <div>
          <label>Customer: <input value={customerName} onChange={e=>setCustomerName(e.target.value)} /></label>
        </div>
        <div>
          <label>Currency: <input value={currency} onChange={e=>setCurrency(e.target.value)} /></label>
        </div>
        <div>
          <button type="submit">Create</button>
        </div>
      </form>
    </div>
  )
}
