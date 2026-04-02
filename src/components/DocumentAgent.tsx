interface DocumentAgentProps { apiUrl: string }
export default function DocumentAgent({ apiUrl }: DocumentAgentProps) {
  return <div className="card"><h2 className="card-title">📄 Document Agent</h2><p>Receive and process candidate documents and CVs.</p></div>
}
