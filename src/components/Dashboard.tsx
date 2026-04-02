import { useState, useEffect } from "react"
import { apiClient } from "../services/api"

interface AgentStatus {
  id: string
  name: string
  type: string
  status: string
  process_status: string
}

interface DashboardProps {
  agents: AgentStatus[]
  apiUrl: string
}

export default function Dashboard({ agents: initialAgents, apiUrl }: DashboardProps) {
  const [stats, setStats] = useState({
    total_agents: 0,
    running_agents: 0,
    total_candidates: 0,
    qualified_candidates: 0,
    cvs_received: 0,
    posts_made_today: 0,
  })
  const [agents, setAgents] = useState<AgentStatus[]>(initialAgents)
  const [loading, setLoading] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<AgentStatus | null>(null)
  const [agentLogs, setAgentLogs] = useState<string[]>([])

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      const candidatesRes = await apiClient.getCandidates()
      const agentsRes = await apiClient.getAgentsStatus()

      const candidates = candidatesRes.data.candidates || []
      const qualified = candidates.filter((c: any) => c.status === "qualifiziert").length
      const cvs = candidates.filter((c: any) => c.cv_status === "received").length

      setAgents(agentsRes.data.agents || [])
      setStats({
        total_agents: agentsRes.data.agents?.length || 0,
        running_agents: agentsRes.data.agents?.filter((a: any) => a.process_status === "running").length || 0,
        total_candidates: candidates.length,
        qualified_candidates: qualified,
        cvs_received: cvs,
        posts_made_today: 0,
      })
    } catch (error) {
      console.error("Failed to fetch stats:", error)
    }
  }

  const handleStartAgent = async (agentId: string) => {
    try {
      setLoading(true)
      await apiClient.startAgent(agentId)
      await fetchStats()
    } catch (error) {
      console.error("Failed to start agent:", error)
      alert("Failed to start agent")
    } finally {
      setLoading(false)
    }
  }

  const handleStopAgent = async (agentId: string) => {
    try {
      setLoading(true)
      await apiClient.stopAgent(agentId)
      await fetchStats()
    } catch (error) {
      console.error("Failed to stop agent:", error)
      alert("Failed to stop agent")
    } finally {
      setLoading(false)
    }
  }

  const handleViewLogs = async (agent: AgentStatus) => {
    try {
      setSelectedAgent(agent)
      const logsRes = await apiClient.getAgentLogs(agent.id, 20)
      setAgentLogs(logsRes.data.logs || [])
    } catch (error) {
      console.error("Failed to fetch logs:", error)
      setAgentLogs(["Failed to load logs"])
    }
  }

  return (
    <div className="dashboard">
      <h2>📊 Dashboard Overview</h2>

      <div className="grid">
        <div className="card">
          <div className="stat-box">
            <div className="stat-value">{stats.total_agents}</div>
            <div className="stat-label">Total Agents</div>
          </div>
        </div>

        <div className="card">
          <div className="stat-box">
            <div className="stat-value" style={{ color: "#00ff88" }}>
              {stats.running_agents}
            </div>
            <div className="stat-label">Running</div>
          </div>
        </div>

        <div className="card">
          <div className="stat-box">
            <div className="stat-value">{stats.total_candidates}</div>
            <div className="stat-label">Total Candidates</div>
          </div>
        </div>

        <div className="card">
          <div className="stat-box">
            <div className="stat-value" style={{ color: "#00ff88" }}>
              {stats.qualified_candidates}
            </div>
            <div className="stat-label">Qualified</div>
          </div>
        </div>

        <div className="card">
          <div className="stat-box">
            <div className="stat-value">{stats.cvs_received}</div>
            <div className="stat-label">CVs Received</div>
          </div>
        </div>

        <div className="card">
          <div className="stat-box">
            <div className="stat-value">{stats.posts_made_today}</div>
            <div className="stat-label">Posts Today</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">🤖 Agent Status & Control</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Agent</th>
              <th>Type</th>
              <th>Status</th>
              <th>Process</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {agents.map(agent => (
              <tr key={agent.id}>
                <td>
                  <strong>{agent.name}</strong>
                  <br />
                  <small style={{ color: "var(--text-secondary)" }}>{agent.id}</small>
                </td>
                <td>{agent.type}</td>
                <td>
                  <span className={`status-badge ${agent.status}`}>
                    {agent.status}
                  </span>
                </td>
                <td>
                  <span className={`status-badge ${agent.process_status}`}>
                    {agent.process_status}
                  </span>
                </td>
                <td style={{ display: "flex", gap: "0.5rem" }}>
                  {agent.process_status === "running" ? (
                    <button
                      className="button button-secondary"
                      onClick={() => handleStopAgent(agent.id)}
                      disabled={loading}
                      style={{ fontSize: "0.85rem", padding: "0.5rem 0.75rem" }}
                    >
                      Stop
                    </button>
                  ) : (
                    <button
                      className="button button-primary"
                      onClick={() => handleStartAgent(agent.id)}
                      disabled={loading}
                      style={{ fontSize: "0.85rem", padding: "0.5rem 0.75rem" }}
                    >
                      Start
                    </button>
                  )}
                  <button
                    className="button button-secondary"
                    onClick={() => handleViewLogs(agent)}
                    style={{ fontSize: "0.85rem", padding: "0.5rem 0.75rem" }}
                  >
                    Logs
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedAgent && (
        <div className="card">
          <h3 className="card-title">📋 Logs: {selectedAgent.name}</h3>
          <div style={{
            background: "var(--background)",
            border: "1px solid var(--border)",
            borderRadius: "4px",
            padding: "1rem",
            maxHeight: "300px",
            overflowY: "auto",
            fontFamily: "monospace",
            fontSize: "0.85rem",
            color: "var(--text-secondary)"
          }}>
            {agentLogs.length > 0 ? (
              agentLogs.map((log, i) => (
                <div key={i} style={{ marginBottom: "0.25rem" }}>
                  {log}
                </div>
              ))
            ) : (
              <div>No logs available</div>
            )}
          </div>
          <button
            className="button button-secondary"
            onClick={() => setSelectedAgent(null)}
            style={{ marginTop: "1rem" }}
          >
            Close
          </button>
        </div>
      )}

      <style>{`
        .dashboard h2 {
          margin-bottom: 2rem;
          color: var(--primary);
        }

        .stat-box {
          text-align: center;
        }

        .stat-value {
          font-size: 2.5rem;
          font-weight: 700;
          color: var(--primary);
          margin-bottom: 0.5rem;
        }

        .stat-label {
          color: var(--text-secondary);
          font-size: 0.95rem;
        }

        .table td {
          vertical-align: middle;
        }

        .table td small {
          display: block;
          margin-top: 0.25rem;
        }
      `}</style>
    </div>
  )
}
