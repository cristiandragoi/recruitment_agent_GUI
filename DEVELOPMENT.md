# Development Guide - Recruitment Agent GUI

**Version:** 1.0.0  
**Last Updated:** April 2, 2026

---

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Architecture](#project-architecture)
3. [Component Development](#component-development)
4. [API Integration](#api-integration)
5. [State Management](#state-management)
6. [Styling Guidelines](#styling-guidelines)
7. [Testing](#testing)
8. [Debugging](#debugging)
9. [Build Process](#build-process)
10. [Deployment](#deployment)

---

## Development Environment Setup

### System Requirements

- **OS:** Windows 10+, macOS 10.13+, or Linux (Ubuntu 18.04+)
- **Node.js:** 16.0 or higher
- **Rust:** Latest stable (for Tauri builds)
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 2GB for dependencies and build artifacts

### Initial Setup

```bash
# Clone repository
git clone https://github.com/cristiandragoi/recruitment_agent_GUI.git
cd recruitment_agent_GUI

# Install dependencies
npm install

# Verify Rust installation
rustc --version
cargo --version

# Start development server
npm run dev
```

### Environment Variables

Create a `.env` file in the project root (not committed to git):

```bash
# Backend API Configuration
VITE_API_URL=http://localhost:8000/api

# Development Settings
VITE_DEBUG=true
VITE_LOG_LEVEL=debug
```

---

## Project Architecture

### Directory Structure

```
src/
├── components/          # React components (one per agent)
├── services/           # API clients and utilities
├── App.tsx            # Main application component
├── main.tsx           # React DOM entry point
└── index.css          # Global styles

src-tauri/            # Tauri backend (Rust)
├── src/
│   └── main.rs       # Tauri window and menu setup
└── tauri.conf.json   # Tauri configuration
```

### Component Hierarchy

```
App
├── Dashboard          # Main overview
├── FacebookScraper    # Agent component
├── DailyPoster        # Agent component
├── EngagementBot      # Agent component
├── DMResponder        # Agent component
├── DocumentAgent      # Agent component
├── Candidates         # Data management
└── Settings           # Configuration
```

### Data Flow

```
User Interaction
    ↓
Component State Update
    ↓
API Call (axios)
    ↓
Backend Processing
    ↓
Response Handling
    ↓
UI Update
```

---

## Component Development

### Creating a New Agent Component

1. **Create Component File**

```typescript
// src/components/MyAgent.tsx
import { useState, useEffect } from "react"
import axios from "axios"

interface AgentConfig {
  id: string
  name: string
  enabled: boolean
  config: Record<string, unknown>
}

export default function MyAgent() {
  const [config, setConfig] = useState<AgentConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const API_URL = "http://localhost:8000/api"

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await axios.get(`${API_URL}/config/my-agent`)
        setConfig(response.data)
      } catch (err) {
        setError("Failed to load configuration")
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchConfig()
  }, [])

  const handleStart = async () => {
    try {
      await axios.post(`${API_URL}/agents/my-agent/start`)
      // Update UI
    } catch (err) {
      setError("Failed to start agent")
    }
  }

  if (loading) return <div className="loading">Loading...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div className="agent-container">
      <h2>{config?.name}</h2>
      <button onClick={handleStart}>Start Agent</button>
    </div>
  )
}
```

2. **Register in App.tsx**

```typescript
import MyAgent from "./components/MyAgent"

// Add to TabType
type TabType = "dashboard" | "my-agent" | ...

// Add to component rendering
{activeTab === "my-agent" && <MyAgent />}

// Add to navigation
<button onClick={() => setActiveTab("my-agent")}>My Agent</button>
```

3. **Add Styling**

```css
/* In src/App.css */
.agent-container {
  padding: 20px;
  border-radius: 8px;
  background: #f5f5f5;
}

.agent-container h2 {
  margin-top: 0;
  color: #333;
}

.agent-container button {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.agent-container button:hover {
  background: #0056b3;
}
```

### Component Best Practices

**Use TypeScript Interfaces:**
```typescript
interface Props {
  agentId: string
  onStatusChange: (status: string) => void
}

export default function Agent({ agentId, onStatusChange }: Props) {
  // Component code
}
```

**Handle Loading and Error States:**
```typescript
if (loading) return <LoadingSpinner />
if (error) return <ErrorMessage message={error} />
return <Content data={data} />
```

**Clean Up Effects:**
```typescript
useEffect(() => {
  const timer = setInterval(() => {
    fetchStatus()
  }, 5000)

  return () => clearInterval(timer) // Cleanup
}, [])
```

---

## API Integration

### API Client Setup

The `src/services/api.ts` file provides a configured Axios instance:

```typescript
import axios from "axios"

const API_URL = "http://localhost:8000/api"

export const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
})

// Add request interceptor for logging
apiClient.interceptors.request.use((config) => {
  console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`)
  return config
})

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error(`[API Error] ${error.message}`)
    return Promise.reject(error)
  }
)
```

### Making API Calls

```typescript
// GET request
const fetchAgents = async () => {
  try {
    const response = await axios.get(`${API_URL}/agents/status`)
    setAgents(response.data.agents)
  } catch (error) {
    console.error("Failed to fetch agents:", error)
  }
}

// POST request
const startAgent = async (agentId: string) => {
  try {
    await axios.post(`${API_URL}/agents/${agentId}/start`)
    // Handle success
  } catch (error) {
    console.error("Failed to start agent:", error)
  }
}

// PUT request with data
const updateConfig = async (agentId: string, config: object) => {
  try {
    await axios.put(`${API_URL}/config/${agentId}`, config)
  } catch (error) {
    console.error("Failed to update config:", error)
  }
}
```

### Error Handling

```typescript
const handleApiCall = async () => {
  try {
    const response = await axios.get(`${API_URL}/endpoint`)
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 404) {
        console.error("Resource not found")
      } else if (error.response?.status === 500) {
        console.error("Server error")
      } else if (error.code === "ECONNABORTED") {
        console.error("Request timeout")
      }
    } else {
      console.error("Unknown error:", error)
    }
    throw error
  }
}
```

---

## State Management

### Using React Hooks

**useState for Local State:**
```typescript
const [count, setCount] = useState(0)
const [agents, setAgents] = useState<Agent[]>([])
const [isLoading, setIsLoading] = useState(false)
```

**useEffect for Side Effects:**
```typescript
useEffect(() => {
  // Run when component mounts
  fetchData()
}, []) // Empty dependency array

useEffect(() => {
  // Run when dependency changes
  console.log("Active tab changed:", activeTab)
}, [activeTab])
```

**useCallback for Memoized Functions:**
```typescript
const handleClick = useCallback(() => {
  console.log("Clicked")
}, []) // Dependencies
```

### State Update Patterns

**Updating Arrays:**
```typescript
// Add item
setAgents([...agents, newAgent])

// Remove item
setAgents(agents.filter(a => a.id !== agentId))

// Update item
setAgents(agents.map(a => 
  a.id === agentId ? { ...a, status: "running" } : a
))
```

**Updating Objects:**
```typescript
// Merge properties
setConfig({ ...config, enabled: true })

// Update nested property
setConfig({
  ...config,
  settings: { ...config.settings, timeout: 5000 }
})
```

---

## Styling Guidelines

### CSS Architecture

Use BEM (Block Element Modifier) naming convention:

```css
/* Block */
.agent-card {
  padding: 20px;
  border-radius: 8px;
  background: white;
}

/* Element */
.agent-card__title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}

.agent-card__status {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

/* Modifier */
.agent-card__status--running {
  background: #d4edda;
  color: #155724;
}

.agent-card__status--stopped {
  background: #f8d7da;
  color: #721c24;
}
```

### Color Palette

```css
:root {
  --primary: #007bff;
  --success: #28a745;
  --warning: #ffc107;
  --danger: #dc3545;
  --dark: #343a40;
  --light: #f8f9fa;
  --border: #dee2e6;
}
```

### Responsive Design

```css
/* Mobile first */
.container {
  padding: 10px;
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    padding: 20px;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    padding: 30px;
  }
}
```

---

## Testing

### Type Checking

```bash
npm run type-check
```

Verify all TypeScript types are correct before building.

### Manual Testing

1. **Test Component Rendering**
   - Verify component appears correctly
   - Check responsive layout on different screen sizes

2. **Test API Integration**
   - Verify API calls are made correctly
   - Check error handling with invalid data
   - Test with backend offline

3. **Test User Interactions**
   - Click buttons and verify actions
   - Test form submissions
   - Verify state updates correctly

### Browser DevTools

**Console Tab:**
- Check for JavaScript errors
- View console.log output
- Test API calls manually

**Network Tab:**
- Monitor API requests
- Check request/response payloads
- Identify slow requests

**Elements Tab:**
- Inspect component structure
- Check applied styles
- Debug layout issues

---

## Debugging

### Enable Debug Logging

```typescript
// In App.tsx
const DEBUG = true

const log = (message: string, data?: unknown) => {
  if (DEBUG) {
    console.log(`[DEBUG] ${message}`, data)
  }
}
```

### Debug API Calls

```typescript
// Add to api.ts
apiClient.interceptors.request.use((config) => {
  console.log("[API Request]", {
    method: config.method,
    url: config.url,
    data: config.data,
  })
  return config
})

apiClient.interceptors.response.use(
  (response) => {
    console.log("[API Response]", {
      status: response.status,
      data: response.data,
    })
    return response
  },
  (error) => {
    console.error("[API Error]", {
      status: error.response?.status,
      message: error.message,
      data: error.response?.data,
    })
    return Promise.reject(error)
  }
)
```

### React DevTools

Install React DevTools browser extension to:
- Inspect component hierarchy
- View component props and state
- Track component re-renders
- Profile performance

---

## Build Process

### Development Build

```bash
npm run dev
```

Starts Tauri dev server with hot reload.

### Production Build

```bash
npm run build
```

Creates optimized production build:
- Bundles React and dependencies
- Minifies JavaScript and CSS
- Generates platform-specific executables
- Creates installer for distribution

### Build Output

- **Windows:** `src-tauri/target/release/Recruitment Agent GUI.exe`
- **Linux:** `src-tauri/target/release/recruitment-agent-gui`
- **macOS:** `src-tauri/target/release/Recruitment Agent GUI.app`

### Build Optimization

The build process includes:
- Tree-shaking to remove unused code
- Code splitting for lazy loading
- Asset compression and minification
- Source map generation for debugging

---

## Deployment

### Release Process

1. **Update Version**
   ```json
   // package.json
   "version": "1.1.0"
   ```

2. **Build Release**
   ```bash
   npm run build
   ```

3. **Create Git Tag**
   ```bash
   git tag -a v1.1.0 -m "Release version 1.1.0"
   git push origin v1.1.0
   ```

4. **Upload Artifacts**
   - Upload executables to GitHub Releases
   - Create release notes
   - Mark as latest release

### Distribution

**Windows Users:**
- Download `.exe` installer
- Run installer to install application
- Application appears in Start Menu

**Linux Users:**
- Download `.AppImage` or `.deb` package
- Make executable: `chmod +x *.AppImage`
- Run or install package

**macOS Users:**
- Download `.dmg` file
- Mount DMG and drag app to Applications folder

---

## Common Development Tasks

### Adding a New Agent Type

1. Create component in `src/components/NewAgent.tsx`
2. Add to App.tsx imports and TabType
3. Add navigation button
4. Implement API integration
5. Test thoroughly

### Updating API Integration

1. Check backend API documentation
2. Update API URL if needed
3. Modify request/response handling
4. Test with actual backend
5. Handle error cases

### Fixing Bugs

1. Identify issue and reproduction steps
2. Check browser console for errors
3. Add debug logging
4. Locate problematic code
5. Implement fix
6. Test fix thoroughly
7. Commit with descriptive message

### Performance Optimization

1. Profile with React DevTools
2. Identify slow components
3. Implement memoization if needed
4. Optimize API calls (debounce, cache)
5. Measure improvement

---

## Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tauri Documentation](https://tauri.app)
- [Vite Documentation](https://vitejs.dev)
- [Axios Documentation](https://axios-http.com)

---

**Last Updated:** April 2, 2026  
**Maintained By:** Manus AI
