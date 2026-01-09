import React, {useEffect, useState} from 'react'
import {useParams} from 'react-router-dom'

export default function InvoiceStatus(){
  const { id } = useParams();
  const [status, setStatus] = useState<any>(null)

  useEffect(()=>{
    if(!id) return
    fetch(`/api/invoices/${id}/status`).then(r=>r.json()).then(setStatus).catch(()=>setStatus({error:'Unable to fetch'}))
  },[id])

  const handleUpload = async (e: any) => {
    e.preventDefault()
    const fileInput = document.getElementById('signed-file') as HTMLInputElement
    if(!fileInput || !fileInput.files || fileInput.files.length===0) return
    const file = fileInput.files[0]
    // request presigned URL
    const resp = await fetch(`/api/invoices/${id}/presign_signed`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({filename: file.name})
    })
    const data = await resp.json()
    const upload = data.upload
    // upload via PUT
    const putResp = await fetch(upload.url, {method:'PUT', body: file, headers: upload.headers})
    if(!putResp.ok){
      alert('Upload failed')
      return
    }
    // tell backend to attach the document record
    const attachResp = await fetch(`/api/invoices/${id}/attach_signed`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({filename: file.name, path: data.storage_path})
    })
    const a = await attachResp.json()
    alert('Uploaded and recorded: ' + JSON.stringify(a))
  }

  return (
    <div>
      <h2>Invoice Status: {id}</h2>
      <pre>{JSON.stringify(status, null, 2)}</pre>
      <div>
        <h3>Upload Signed Document</h3>
        <input id="signed-file" type="file" />
        <button onClick={handleUpload}>Upload</button>
      </div>
    </div>
  )
}
