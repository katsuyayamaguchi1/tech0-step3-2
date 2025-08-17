'use client';

import { useEffect, useState } from 'react';

export default function SamplePage() {
  const API = process.env.NEXT_PUBLIC_API_URL; // .env.local から
  const [rows, setRows] = useState([]);
  const [name, setName] = useState('');

  const fetchList = async () => {
    const res = await fetch(`${API}/sample`, { cache: 'no-store' });
    const data = await res.json();
    setRows(data);
  };

  const add = async () => {
    if (!name) return;
    await fetch(`${API}/sample`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    });
    setName('');
    fetchList();
  };

  useEffect(() => { fetchList(); }, []);

  return (
    <main style={{ maxWidth: 640, margin: '40px auto', fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ fontSize: 24, fontWeight: 700 }}>Sample CRUD (FastAPI)</h1>

      <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="name"
          style={{ flex: 1, padding: 8, border: '1px solid #ddd', borderRadius: 8 }}
        />
        <button onClick={add} style={{ padding: '8px 16px', borderRadius: 8, border: '1px solid #ddd' }}>
          Add
        </button>
      </div>

      <ul style={{ marginTop: 24, padding: 0, listStyle: 'none' }}>
        {rows.map(r => (
          <li key={r.id} style={{ padding: 12, border: '1px solid #eee', borderRadius: 8, marginBottom: 8 }}>
            <div style={{ fontWeight: 600 }}>{r.name}</div>
            <div style={{ fontSize: 12, color: '#666' }}>{new Date(r.created_at).toLocaleString()}</div>
          </li>
        ))}
      </ul>
    </main>
  );
}

