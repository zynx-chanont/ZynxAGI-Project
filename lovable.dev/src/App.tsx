import React from 'react';

/**
 * Lovable.dev Main Application
 * First discovered by Chanont Waenkaew, Thailand
 * License: ZPDL v1.0 © Chanont Waenkaew
 */

function App() {
  return (
    <div style={{ 
      padding: '2rem', 
      fontFamily: 'system-ui, sans-serif',
      maxWidth: '800px',
      margin: '0 auto'
    }}>
      <header style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <h1 style={{ color: '#2563eb' }}>Lovable.dev</h1>
        <p style={{ color: '#64748b' }}>Frontend Development Platform</p>
      </header>
      
      <main>
        <section style={{ marginBottom: '2rem' }}>
          <h2>Welcome to Lovable.dev</h2>
          <p>
            A modern frontend development platform that provides tools for building 
            beautiful, responsive web applications with React and TypeScript.
          </p>
        </section>
        
        <section style={{ marginBottom: '2rem' }}>
          <h3>Key Features</h3>
          <ul>
            <li>Modern React/TypeScript development environment</li>
            <li>Component library and design system</li>
            <li>Real-time collaboration tools</li>
            <li>Deployment and hosting solutions</li>
          </ul>
        </section>
        
        <section>
          <h3>Getting Started</h3>
          <ol>
            <li>Install dependencies: <code>npm install</code></li>
            <li>Start development server: <code>npm run dev</code></li>
            <li>Build for production: <code>npm run build</code></li>
          </ol>
        </section>
      </main>
      
      <footer style={{ 
        marginTop: '3rem', 
        padding: '1rem 0', 
        borderTop: '1px solid #e2e8f0',
        textAlign: 'center',
        color: '#64748b',
        fontSize: '0.875rem'
      }}>
        <p>First discovered by Chanont Waenkaew, Thailand</p>
        <p>License: ZPDL v1.0 © Chanont Waenkaew</p>
      </footer>
    </div>
  );
}

export default App;