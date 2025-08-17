'use client';
import { useEffect, useState } from 'react';

export default function StatusPage() {
  const API = process.env.NEXT_PUBLIC_API_URL;
  const [db, setDb] = useState(null);
  const [info, setInfo] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const r1 = await fetch(`${API}/health/db`, { cache: 'no-store' });
        const r2 = await fetch(`${API}/health/info`, { cache: 'no-store' });
        setDb(await r1.json());
        setInfo(await r2.json());
      } catch (e) { setErr(String(e)); }
    })();
  }, [API]);

  return (
    <main style={{maxWidth:720,margin:'40px auto',fontFamily:'system-ui,sans-serif'}}>
      <h1 style={{fontSize:24,fontWeight:700}}>System Status</h1>

      <div style={{display:'flex',alignItems:'center',gap:8,marginTop:16}}>
        <span style={{
          width:12,height:12,borderRadius:'50%',
          background: db?.db==='ok' ? 'limegreen' : 'orangered'
        }}/>
        <span>Backend → DB: {db?.db || '...'}</span>
      </div>

      {info && (
        <pre style={{background:'#f7f7f7',padding:12,borderRadius:8,marginTop:12}}>
{JSON.stringify(info, null, 2)}
        </pre>
      )}

      {err && <div style={{color:'crimson',marginTop:12}}>Error: {err}</div>}
    </main>
  );
}

