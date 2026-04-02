import { useState, useEffect } from "react"
import { appWindow } from "@tauri-apps/api/window"
import axios from "axios"
import { apiClient } from "./services/api"
import "./App.css"

// Components
import Dashboard from "./components/Dashboard"
import FacebookScraper from "./components/FacebookScraper"
import DailyPoster from "./components/DailyPoster"
import EngagementBot from "./components/EngagementBot"
import DMResponder from "./components/DMResponder"
import DocumentAgent from "./components/DocumentAgent"
import Candidates from "./components/Candidates"
import Settings from "./components/Settings"

type TabType = "dashboard" | "scraper" | "poster" | "engagement" | "dm" | "documents" | "candidates" | "settings"

interface AgentStatus {
  id: string
  name: string
  type: string
  status: string
  process_status: string
}

function App() {
  const [activeTab, setActiveTab] = useState<TabType>("dashboard")
  const [agents, setAgents] = useState<AgentStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [serverConnected, setServerConnected] = useState(false)

  const API_URL = "http://localhost:8000/api"

  // Fetch agent status
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await axios.get(`${API_URL}/agents/status`)
        setAgents(response.data.agents)
        setServerConnected(true)
      } catch (error) {
        console.error("Failed to connect to agent server:", error)
        setServerConnected(false)
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, 5000) // Refresh every 5 seconds

    return () => clearInterval(interval)
  }, [])

  // Minimize to tray
  const minimizeToTray = async () => {
    await appWindow.hide()
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <h1>🚀 OpenClaw</h1>
          <span className="subtitle">Recruitment Automation</span>
        </div>
        <div className="header-right">
          <div className={`server-status ${serverConnected ? "connected" : "disconnected"}`}>
            <span className="status-dot"></span>
            {serverConnected ? "Connected" : "Disconnected"}
          </div>
          <button className="minimize-btn" onClick={minimizeToTray} title="Minimize to tray">
            −
          </button>
        </div>
      </header>

      <div className="app-container">
        <nav className="sidebar">
          <div className="nav-section">
            <h3>Agents</h3>
            <button
              className={`nav-item ${activeTab === "dashboard" ? "active" : ""}`}
              onClick={() => setActiveTab("dashboard")}
            >
              📊 Dashboard
            </button>
            <button
              className={`nav-item ${activeTab === "scraper" ? "active" : ""}`}
              onClick={() => setActiveTab("scraper")}
            >
              🔍 Facebook Scraper
            </button>
            <button
              className={`nav-item ${activeTab === "poster" ? "active" : ""}`}
              onClick={() => setActiveTab("poster")}
            >
              📝 Daily Poster
            </button>
            <button
              className={`nav-item ${activeTab === "engagement" ? "active" : ""}`}
              onClick={() => setActiveTab("engagement")}
            >
              💬 Engagement Bot
            </button>
            <button
              className={`nav-item ${activeTab === "dm" ? "active" : ""}`}
              onClick={() => setActiveTab("dm")}
            >
              📱 DM Responder
            </button>
            <button
              className={`nav-item ${activeTab === "documents" ? "active" : ""}`}
              onClick={() => setActiveTab("documents")}
            >
              📄 Document Agent
            </button>
          </div>

          <div className="nav-section">
            <h3>Data</h3>
            <button
              className={`nav-item ${activeTab === "candidates" ? "active" : ""}`}
              onClick={() => setActiveTab("candidates")}
            >
              👥 Candidates
            </button>
          </div>

          <div className="nav-section">
            <h3>System</h3>
            <button
              className={`nav-item ${activeTab === "settings" ? "active" : ""}`}
              onClick={() => setActiveTab("settings")}
            >
              ⚙️ Settings
            </button>
          </div>
        </nav>

        <main className="main-content">
          {loading ? (
            <div className="loading">Loading agent status...</div>
          ) : (
            <>
              {activeTab === "dashboard" && <Dashboard agents={agents} apiUrl={API_URL} />}
              {activeTab === "scraper" && <FacebookScraper apiUrl={API_URL} />}
              {activeTab === "poster" && <DailyPoster apiUrl={API_URL} />}
              {activeTab === "engagement" && <EngagementBot apiUrl={API_URL} />}
              {activeTab === "dm" && <DMResponder apiUrl={API_URL} />}
              {activeTab === "documents" && <DocumentAgent apiUrl={API_URL} />}
              {activeTab === "candidates" && <Candidates apiUrl={API_URL} />}
              {activeTab === "settings" && <Settings apiUrl={API_URL} />}
            </>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
