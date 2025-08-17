'use client';
import { useEffect, useState } from 'react';

export default function CustomersPage() {
  const API = process.env.NEXT_PUBLIC_API_URL;
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState({ customer_id: '', customer_name: '', age: 0, gender: 'male' });
  const [loading, setLoading] = useState(false);

  const fetchAll = async () => {
    const res = await fetch(`${API}/allcustomers`, { cache: 'no-store' });
    const data = await res.json();
    setRows(Array.isArray(data) ? data : []);
  };

  const create = async () => {
    if (!form.customer_id || !form.customer_name) return;
    setLoading(true);
    await fetch(`${API}/customers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form, age: Number(form.age) }),
    });
    setForm({ customer_id: '', customer_name: '', age: 0, gender: 'male' });
    await fetchAll();
    setLoading(false);
  };

  const update = async () => {
    if (!form.customer_id) return;
    setLoading(true);
    await fetch(`${API}/customers`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form, age: Number(form.age) }),
    });
    await fetchAll();
    setLoading(false);
  };

  const remove = async (id) => {
    setLoading(true);
    await fetch(`${API}/customers?customer_id=${encodeURIComponent(id)}`, { method: 'DELETE' });
    await fetchAll();
    setLoading(false);
  };

  const fill = (r) => setForm({ ...r });

  useEffect(() => { fetchAll(); }, []);

  return (
    <main style={{ maxWidth: 800, margin: '40px auto', fontFamily: 'system-ui,sans-serif' }}>
      <h1 style={{ fontSize: 24, fontWeight: 700 }}>Customers</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 16 }}>
        <input placeholder="customer_id" value={form.customer_id}
          onChange={e=>setForm(f=>({...f, customer_id:e.target.value}))} />
        <input placeholder="customer_name" value={form.customer_name}
          onChange={e=>setForm(f=>({...f, customer_name:e.target.value}))} />
        <input placeholder="age" type="number" value={form.age}
          onChange={e=>setForm(f=>({...f, age:e.target.value}))} />
        <select value={form.gender} onChange={e=>setForm(f=>({...f, gender:e.target.value}))}>
          <option value="male">male</option><option value="female">female</option>
        </select>
      </div>

      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
        <button onClick={create} disabled={loading}>Create</button>
        <button onClick={update} disabled={loading}>Update</button>
      </div>

      <ul style={{ marginTop: 24, padding: 0, listStyle: 'none' }}>
        {rows.map(r => (
          <li key={r.customer_id} style={{ padding: 12, border: '1px solid #eee', borderRadius: 8, marginBottom: 8 }}>
            <div><b>{r.customer_id}</b> — {r.customer_name} / {r.age} / {r.gender}</div>
            <div style={{ marginTop: 6 }}>
              <button onClick={()=>fill(r)} style={{ marginRight: 8 }}>Edit</button>
              <button onClick={()=>remove(r.customer_id)}>Delete</button>
            </div>
          </li>
        ))}
      </ul>
    </main>
  );
}
