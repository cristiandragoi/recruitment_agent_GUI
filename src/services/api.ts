import axios, { AxiosInstance } from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  // Health check
  async healthCheck() {
    return this.client.get('/health')
  }

  // Agent endpoints
  async getAgentsStatus() {
    return this.client.get('/agents/status')
  }

  async startAgent(agentId: string) {
    return this.client.post(`/agents/${agentId}/start`)
  }

  async stopAgent(agentId: string) {
    return this.client.post(`/agents/${agentId}/stop`)
  }

  async restartAgent(agentId: string) {
    return this.client.post(`/agents/${agentId}/restart`)
  }

  async searchGroups(agentId: string, keywords: string[]) {
    return this.client.post(`/agents/${agentId}/search-groups`, { keywords })
  }

  async contactCandidate(agentId: string, candidateId: string, message: string) {
    return this.client.post(`/agents/${agentId}/contact-candidate`, {
      candidate_id: candidateId,
      message,
    })
  }

  async postToGroup(agentId: string, groupId: string, content: string) {
    return this.client.post(`/agents/${agentId}/post-to-group`, {
      group_id: groupId,
      content,
    })
  }

  // Configuration endpoints
  async getConfig() {
    return this.client.get('/config')
  }

  async updateConfig(config: any) {
    return this.client.post('/config', config)
  }

  async getAgentConfig(agentId: string) {
    return this.client.get(`/config/${agentId}`)
  }

  // Logs endpoints
  async getAgentLogs(agentId: string, tail: number = 50) {
    return this.client.get(`/logs/${agentId}?tail=${tail}`)
  }

  // Candidate endpoints
  async getCandidates() {
    return this.client.get('/candidates')
  }

  async getCandidate(candidateId: string) {
    return this.client.get(`/candidates/${candidateId}`)
  }

  async createCandidate(candidate: any) {
    return this.client.post('/candidates', candidate)
  }

  async updateCandidate(candidateId: string, candidate: any) {
    return this.client.put(`/candidates/${candidateId}`, candidate)
  }

  // Conversation endpoints
  async getConversations(candidateId: string) {
    return this.client.get(`/conversations/${candidateId}`)
  }

  async addMessage(candidateId: string, agentId: string, message: string, sender: string) {
    return this.client.post('/conversations', {
      candidate_id: candidateId,
      agent_id: agentId,
      message,
      sender,
    })
  }

  // Ollama endpoints
  async getOllamaModels() {
    return this.client.get('/ollama/models')
  }

  async selectOllamaModel(model: string) {
    return this.client.post('/ollama/select-model', { model })
  }

  // Reports endpoints
  async getDailyReports() {
    return this.client.get('/reports/daily')
  }

  // Test endpoints
  async generateMockData() {
    return this.client.post('/test/generate-mock-data')
  }
}

export const apiClient = new ApiClient()
