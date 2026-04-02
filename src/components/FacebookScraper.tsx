interface FacebookScraperProps {
  apiUrl: string
}

export default function FacebookScraper({ apiUrl }: FacebookScraperProps) {
  return (
    <div className="card">
      <h2 className="card-title">🔍 Facebook Scraper Agent</h2>
      <p>Monitor Facebook groups for recruitment opportunities and automatically contact candidates.</p>
      <div style={{ marginTop: "1rem", color: "var(--text-secondary)" }}>
        <p>Status: Ready</p>
        <p>Groups Monitored: 0</p>
        <p>Candidates Found: 0</p>
      </div>
    </div>
  )
}
