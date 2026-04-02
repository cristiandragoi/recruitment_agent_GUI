import { useState, useEffect } from "react"
import { apiClient } from "../services/api"

interface Candidate {
  id: string
  name: string
  country: string
  position: string
  status: string
  cv_status: string
  whatsapp?: string
  german_level?: string
  experience?: number
  contact_date?: string
}

interface CandidatesProps {
  apiUrl: string
}

export default function Candidates({ apiUrl }: CandidatesProps) {
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null)
  const [conversations, setConversations] = useState<any[]>([])
  const [filterStatus, setFilterStatus] = useState<string>("all")

  useEffect(() => {
    fetchCandidates()
    const interval = setInterval(fetchCandidates, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchCandidates = async () => {
    try {
      const response = await apiClient.getCandidates()
      setCandidates(response.data.candidates || [])
    } catch (error) {
      console.error("Failed to fetch candidates:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectCandidate = async (candidate: Candidate) => {
    setSelectedCandidate(candidate)
    try {
      const convsRes = await apiClient.getConversations(candidate.id)
      setConversations(convsRes.data.messages || [])
    } catch (error) {
      console.error("Failed to fetch conversations:", error)
      setConversations([])
    }
  }

  const filteredCandidates = filterStatus === "all"
    ? candidates
    : candidates.filter(c => c.status === filterStatus)

  const statusOptions = ["all", "contacted", "antwort_erhalten", "qualifiziert", "nicht_geeignet", "cv_angefordert"]

  if (loading) return <div className="loading">Loading candidates...</div>

  return (
    <div className="candidates-container">
      <div className="card">
        <h2 className="card-title">👥 Candidates ({filteredCandidates.length})</h2>

        <div className="form-group" style={{ marginBottom: "1rem" }}>
          <label>Filter by Status</label>
          <select
            value={filterStatus}
            onChange={e => setFilterStatus(e.target.value)}
            className="input"
          >
            {statusOptions.map(status => (
              <option key={status} value={status}>
                {status === "all" ? "All Statuses" : status}
              </option>
            ))}
          </select>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Country</th>
                <th>Position</th>
                <th>Experience</th>
                <th>German</th>
                <th>Status</th>
                <th>CV</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredCandidates.map(candidate => (
                <tr key={candidate.id}>
                  <td><strong>{candidate.name}</strong></td>
                  <td>{candidate.country}</td>
                  <td>{candidate.position}</td>
                  <td>{candidate.experience || "N/A"} years</td>
                  <td>{candidate.german_level || "N/A"}</td>
                  <td><span className={`status-badge ${candidate.status}`}>{candidate.status}</span></td>
                  <td><span className={`status-badge ${candidate.cv_status}`}>{candidate.cv_status}</span></td>
                  <td>
                    <button
                      className="button button-primary"
                      onClick={() => handleSelectCandidate(candidate)}
                      style={{ fontSize: "0.85rem", padding: "0.5rem 0.75rem" }}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedCandidate && (
        <div className="card">
          <h3 className="card-title">💬 Conversation: {selectedCandidate.name}</h3>

          <div style={{
            background: "var(--background)",
            border: "1px solid var(--border)",
            borderRadius: "4px",
            padding: "1rem",
            maxHeight: "400px",
            overflowY: "auto",
            marginBottom: "1rem"
          }}>
            {conversations.length > 0 ? (
              conversations.map((msg, i) => (
                <div
                  key={i}
                  style={{
                    marginBottom: "1rem",
                    padding: "0.75rem",
                    background: msg.sender === "agent" ? "rgba(0, 212, 255, 0.1)" : "rgba(0, 255, 136, 0.1)",
                    borderLeft: `3px solid ${msg.sender === "agent" ? "var(--primary)" : "var(--success)"}`,
                    borderRadius: "4px"
                  }}
                >
                  <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "0.25rem" }}>
                    <strong>{msg.sender === "agent" ? "🤖 Agent" : "👤 Candidate"}</strong>
                    {msg.timestamp && ` • ${new Date(msg.timestamp).toLocaleString()}`}
                  </div>
                  <div>{msg.message}</div>
                </div>
              ))
            ) : (
              <div style={{ color: "var(--text-secondary)" }}>No conversations yet</div>
            )}
          </div>

          <div style={{ display: "flex", gap: "1rem" }}>
            <button
              className="button button-secondary"
              onClick={() => setSelectedCandidate(null)}
            >
              Close
            </button>
            <button
              className="button button-primary"
              onClick={() => alert("WhatsApp integration coming soon")}
            >
              Send WhatsApp
            </button>
          </div>
        </div>
      )}

      <style>{`
        .candidates-container {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
      `}</style>
    </div>
  )
}
