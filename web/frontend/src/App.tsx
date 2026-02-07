import React, { useState, useEffect } from 'react';
import './App.css';

interface Header {
  name: string;
  email: string;
  phone: string;
  title: string;
  linkedin?: string;
}

interface Role {
  role: string;
  employment: string;
  company: string;
  start: string;
  end: string | null;
  location: string;
  done: string;
  stack: string;
}

interface ResumeData {
  header: Header;
  roles: Role[];
}

function App() {
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/resume')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch resume data');
        }
        return response.json();
      })
      .then(data => {
        setResumeData(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="loading">Loading resume...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!resumeData) {
    return <div className="error">No resume data available</div>;
  }

  return (
    <div className="resume">
      <header className="header">
        <h1>{resumeData.header.name}</h1>
        <p className="title">{resumeData.header.title}</p>
        <div className="contact">
          <p>Email: {resumeData.header.email}</p>
          <p>Phone: {resumeData.header.phone}</p>
          {resumeData.header.linkedin && (
            <p>LinkedIn: <a href={resumeData.header.linkedin} target="_blank" rel="noopener noreferrer">{resumeData.header.linkedin}</a></p>
          )}
        </div>
      </header>

      <section className="experience">
        <h2>Professional Experience</h2>
        {resumeData.roles.map((role, index) => (
          <div key={index} className="role">
            <div className="role-header">
              <h3>{role.role}</h3>
              <div className="role-details">
                <span className="company">{role.company}</span>
                <span className="employment-type">{role.employment}</span>
                <span className="location">{role.location}</span>
                <span className="dates">
                  {role.start} - {role.end || 'Present'}
                </span>
              </div>
            </div>
            <div className="responsibilities">
              <pre>{role.done}</pre>
            </div>
            <div className="tech-stack">
              <strong>Technologies:</strong> {role.stack}
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}

export default App;
