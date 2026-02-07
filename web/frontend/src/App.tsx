import React, {useEffect, useState} from 'react'

type Resume = any

export default function App() {
  const [resume, setResume] = useState<Resume | null>(null)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/resume')
      .then(r => r.json())
      .then(setResume)
      .catch(e => setErr(String(e)))
  }, [])

  if (err) return <div className="app">Error: {err}</div>
  if (!resume) return <div className="app">Loading resume…</div>

  const header = resume.header || {}
  const roles = resume.roles || []

  return (
    <div className="app">
      <div className="resume">
        <header className="resume-header">
          <h1>{header.name}</h1>
          <div className="meta">{header.title} — {header.email} — {header.phone}</div>
        </header>

        <section className="section">
          <h2>Experience</h2>
          {roles.map((r: any, i: number) => (
            <article key={i} className="role">
              <h3>{r.role} @ {r.company}</h3>
              <div className="when">{r.start} — {r.end || 'Present'} • {r.location}</div>
              <pre className="done">{r.done}</pre>
            </article>
          ))}
        </section>
      </div>
    </div>
  )
}
