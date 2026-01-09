import React from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import InvoiceList from './InvoiceList'
import InvoiceForm from './InvoiceForm'
import Reports from './Reports'
import InvoiceStatus from './InvoiceStatus'

export default function App(){
  return (
    <BrowserRouter>
      <div style={{padding:20}}>
        <h1>Biznooks Frontend (prototype)</h1>
        <nav style={{marginBottom:10}}>
          <Link to="/invoices" style={{marginRight:10}}>Invoices</Link>
          <Link to="/invoices/new" style={{marginRight:10}}>Create Invoice</Link>
          <Link to="/reports">Reports</Link>
        </nav>
        <Routes>
          <Route path="/invoices" element={<InvoiceList/>} />
          <Route path="/invoices/new" element={<InvoiceForm/>} />
          <Route path="/invoices/:id" element={<InvoiceStatus/>} />
          <Route path="/reports" element={<Reports/>} />
          <Route path="/" element={<InvoiceList/>} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
