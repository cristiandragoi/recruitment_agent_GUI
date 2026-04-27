# Recruitment Agent GUI

**Version:** 1.0.0  
**Repository:** https://github.com/cristiandragoi/recruitment_agent_GUI  
**Status:** Active Development  
**Last Updated:** April 2, 2026

---

## Overview

Recruitment Agent GUI is a cross-platform desktop application built with Tauri and React that provides a comprehensive control panel for managing autonomous recruitment agents. The application enables users to monitor, configure, and control multiple AI agents that automate various recruitment tasks including candidate sourcing, job posting, engagement, and communication.

## Project Structure

```
recruitment_agent_GUI/
├── src/                          # React source code
│   ├── components/               # React components for each agent
│   │   ├── Dashboard.tsx         # Main dashboard with agent overview
│   │   ├── FacebookScraper.tsx   # Facebook group monitoring agent
│   │   ├── DailyPoster.tsx       # Job posting automation agent
│   │   ├── EngagementBot.tsx     # Comment engagement agent
│   │   ├── DMResponder.tsx       # Direct message handling agent
│   │   ├── DocumentAgent.tsx     # Document processing agent
│   │   ├── Candidates.tsx        # Candidate management interface
│   │   └── Settings.tsx          # Application settings
│   ├── services/
│   │   └── api.ts                # API client for backend communication
│   ├── App.tsx                   # Main application component
│   ├── App.css                   # Global application styles
│   ├── main.tsx                  # React entry point
│   └── index.css                 # Base styles
├── src-tauri/                    # Tauri backend configuration
├── public/                       # Static assets
├── index.html                    # HTML entry point
├── package.json                  # Project dependencies and scripts
├── tauri.conf.json              # Tauri configuration
├── vite.config.ts               # Vite build configuration
├── tsconfig.json                # TypeScript configuration
└── .gitignore                   # Git ignore rules

```

## Core Components

### 1. Dashboard
The main interface displaying real-time status of all agents, system health metrics, and quick access to agent controls.

**Features:**
- Agent status overview (running, paused, error)
- System health indicators
- Quick start/stop controls
- Real-time activity feed

### 2. Facebook Scraper Agent
Monitors Facebook groups for recruitment opportunities and automatically extracts candidate information.

**Capabilities:**
- Search Facebook groups by keywords
- Extract candidate profiles and contact information
- Automatic candidate contact initiation
- Status tracking and logging

### 3. Daily Poster Agent
Schedules and publishes job advertisements to Facebook groups at optimal times.

**Capabilities:**
- Create and schedule job posts
- Multi-group posting support
- Human-in-the-loop approval workflow
- Post performance tracking

### 4. Engagement Bot Agent
Automatically responds to comments on job posts and engages with interested candidates.

**Capabilities:**
- Monitor post comments in real-time
- Automated response generation
- Candidate qualification through conversation
- Engagement metrics tracking

### 5. DM Responder Agent
Handles direct messages from interested candidates and provides job information.

**Capabilities:**
- Monitor incoming direct messages
- Provide job details and requirements
- Candidate qualification through Q&A
- Interview scheduling

### 6. Document Agent
Processes and analyzes candidate documents (CVs, cover letters).

**Capabilities:**
- Document parsing and extraction
- Candidate qualification scoring
- Information organization and storage

### 7. Candidates Management
Central interface for viewing, organizing, and managing all candidate data.

**Features:**
- Candidate list with filtering and search
- Detailed candidate profiles
- Status tracking (contacted, qualified, rejected)
- CV management
- Communication history

### 8. Settings
Configuration panel for application preferences and agent settings.

**Options:**
- API endpoint configuration
- Agent parameters
- Notification preferences
- Export/import settings

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Desktop Framework** | Tauri | 1.6.3 |
| **UI Framework** | React | 18.3.1 |
| **Build Tool** | Vite | 5.4.21 |
| **Language** | TypeScript | 5.9.3 |
| **HTTP Client** | Axios | 1.14.0 |
| **Styling** | CSS3 | Native |

## Prerequisites

Before running the application, ensure you have the following installed:

- **Node.js** 16.0 or higher
- **npm** or **pnpm** (package manager)
- **Rust** (required for Tauri desktop builds)
  - Install from https://rustup.rs/
- **Backend API Server** running at `http://localhost:8000`

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/cristiandragoi/recruitment_agent_GUI.git
cd recruitment_agent_GUI
```

### 2. Install Dependencies

Using npm:
```bash
npm install
```

Or using pnpm:
```bash
pnpm install
```

### 3. Verify Backend Connection

Ensure the backend API server is running:
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-02T12:16:26.494359",
  "agents_running": 0
}
```

## Running the Application

### Development Mode

Start the Tauri development server with hot-reload:

```bash
npm run dev
```

Or with pnpm:
```bash
pnpm dev
```

The application window will open automatically. The development server supports hot module replacement (HMR) for rapid development iteration.

### Building for Production

Create optimized production builds for Windows and Linux:

```bash
npm run build
```

Or with pnpm:
```bash
pnpm build
```

Build artifacts will be created in the `src-tauri/target/release/` directory.

### Preview Build

Test the production build locally:

```bash
npm run preview
```

## Type Checking

Verify TypeScript types without building:

```bash
npm run type-check
```

## Configuration

### Backend API URL

The application connects to the backend API at `http://localhost:8000/api`. To change this:

1. Open `src/App.tsx`
2. Locate the line: `const API_URL = "http://localhost:8000/api"`
3. Update the URL as needed

### Tauri Configuration

Desktop-specific settings are configured in `tauri.conf.json`:

```json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devPath": "http://localhost:5173",
    "frontendDist": "../dist"
  },
  "app": {
    "windows": [
      {
        "title": "Recruitment Agent GUI",
        "width": 1400,
        "height": 900,
        "resizable": true,
        "fullscreen": false
      }
    ]
  }
}
```

## API Integration

The application communicates with the backend API through the `src/services/api.ts` module. Key endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/agents/status` | GET | Get all agents status |
| `/api/agents/{id}/start` | POST | Start an agent |
| `/api/agents/{id}/stop` | POST | Stop an agent |
| `/api/candidates` | GET | List all candidates |
| `/api/activity-feed` | GET | Get real-time activity |
| `/api/export/candidates-excel` | GET | Export candidates |

## Development Workflow

### 1. Component Development

Create new components in `src/components/`:

```typescript
import { useState, useEffect } from "react"
import axios from "axios"

export default function MyAgent() {
  const [data, setData] = useState(null)
  const API_URL = "http://localhost:8000/api"

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`${API_URL}/endpoint`)
        setData(response.data)
      } catch (error) {
        console.error("Error:", error)
      }
    }
    fetchData()
  }, [])

  return <div>{/* Component JSX */}</div>
}
```

### 2. Styling

Add component-specific styles to `src/App.css` or create component-scoped CSS modules.

### 3. Type Safety

Always define TypeScript interfaces for API responses:

```typescript
interface AgentStatus {
  id: string
  name: string
  type: string
  status: "running" | "paused" | "error"
}
```

### 4. Testing

Run type checking before committing:

```bash
npm run type-check
```

## Troubleshooting

### Backend Connection Error

**Problem:** Application shows "Failed to connect to agent server"

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check API URL in `src/App.tsx`
3. Ensure no firewall blocking port 8000
4. Restart the backend server

### Build Failures

**Problem:** `npm run build` fails with Rust errors

**Solution:**
1. Ensure Rust is installed: `rustc --version`
2. Update Rust: `rustup update`
3. Clear build cache: `rm -rf src-tauri/target`
4. Rebuild: `npm run build`

### Hot Reload Not Working

**Problem:** Changes to code don't reflect in development mode

**Solution:**
1. Verify Vite dev server is running on port 5173
2. Check browser console for errors
3. Restart dev server: `npm run dev`
4. Clear browser cache (Ctrl+Shift+Delete)

### TypeScript Errors

**Problem:** TypeScript compilation errors during build

**Solution:**
1. Run type check: `npm run type-check`
2. Fix reported errors
3. Ensure all imports are correct
4. Verify tsconfig.json is valid

## Git Workflow

This repository is the single source of truth for the Recruitment Agent GUI project. Follow this workflow for development:

### 1. Create Feature Branch

```bash
git checkout -b feature/agent-name
```

### 2. Make Changes

Implement your feature or fix.

### 3. Commit Changes

```bash
git add .
git commit -m "feat: Add new agent component"
```

### 4. Push to Remote

```bash
git push origin feature/agent-name
```

### 5. Create Pull Request

Submit PR on GitHub for review.

## Security Considerations

- **No Secrets in Code:** Never commit API keys, tokens, or passwords
- **Environment Variables:** Use `.env` files (added to .gitignore) for sensitive data
- **API Authentication:** Backend API should implement proper authentication
- **Data Privacy:** Handle candidate data according to privacy regulations

## Performance Optimization

### Build Size

The production build is optimized using:
- Tree-shaking to remove unused code
- Minification of JavaScript and CSS
- Asset compression

### Runtime Performance

- Lazy loading of components
- Efficient state management
- Memoization of expensive computations
- Debouncing of API calls

## Contributing

When contributing to this project:

1. Follow the existing code style and structure
2. Add TypeScript types for all functions and components
3. Test changes locally before committing
4. Write clear commit messages
5. Update documentation as needed

## Future Enhancements

Planned features for future releases:

- Multi-user support with role-based access control
- Advanced analytics and reporting dashboard
- Integration with external ATS systems
- Mobile app version
- Webhook support for external integrations
- Custom agent templates
- Batch operations and bulk imports

## Support

For issues, questions, or suggestions:

1. Check existing GitHub issues
2. Review troubleshooting section above
3. Create a new GitHub issue with detailed description
4. Contact the development team

## License

This project is proprietary and confidential.

## Repository Information

- **Repository URL:** https://github.com/cristiandragoi/recruitment_agent_GUI
- **Main Branch:** main
- **Current Commit:** c4a6b82
- **Last Verified:** April 2, 2026

---

**Last Updated:** April 2, 2026  
**Maintained By:** Manus AI  
**Status:** ✅ Active Development
