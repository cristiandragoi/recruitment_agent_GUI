import { useState, useEffect } from "react"
import axios from "axios"

interface SettingsProps {
  apiUrl: string
}

export default function Settings({ apiUrl }: SettingsProps) {
  const [config, setConfig] = useState<any>({})
  const [loading, setLoading] = useState(true)
  const [ollamaModels, setOllamaModels] = useState<string[]>([])

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const configRes = await axios.get(`${apiUrl}/config`)
        setConfig(configRes.data.config)

        const modelsRes = await axios.get(`${apiUrl}/ollama/models`)
        setOllamaModels(modelsRes.data.models || [])
      } catch (error) {
        console.error("Failed to fetch settings:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchConfig()
  }, [apiUrl])

  const handleSaveConfig = async () => {
    try {
      await axios.post(`${apiUrl}/config`, config)
      alert("Configuration saved!")
    } catch (error) {
      alert("Failed to save configuration")
    }
  }

  if (loading) return <div className="loading">Loading settings...</div>

  return (
    <div className="card">
      <h2 className="card-title">⚙️ Settings</h2>

      <div className="form-group">
        <label>Ollama Model</label>
        <select
          value={config.ollama?.model || "qwen:3.5"}
          onChange={e => setConfig({ ...config, ollama: { ...config.ollama, model: e.target.value } })}
          className="input"
        >
          {ollamaModels.map(model => (
            <option key={model} value={model}>{model}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Ollama Temperature</label>
        <input
          type="number"
          min="0"
          max="1"
          step="0.1"
          value={config.ollama?.temperature || 0.7}
          onChange={e => setConfig({ ...config, ollama: { ...config.ollama, temperature: parseFloat(e.target.value) } })}
          className="input"
        />
      </div>

      <div className="form-group">
        <label>Facebook Email</label>
        <input
          type="email"
          value={config.facebook?.credentials?.email || ""}
          onChange={e => setConfig({
            ...config,
            facebook: {
              ...config.facebook,
              credentials: { ...config.facebook?.credentials, email: e.target.value }
            }
          })}
          className="input"
        />
      </div>

      <button className="button button-primary" onClick={handleSaveConfig}>
        Save Settings
      </button>
    </div>
  )
}
