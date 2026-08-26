# Legal Case Search Frontend

React + TypeScript + Vite frontend application for searching legal cases with vector similarity, RAG, and AI agents.

## Features

- **Vector Search**: Fast semantic search using embeddings
- **RAG (Retrieval-Augmented Generation)**: Grounded answers backed by case citations
- **AI Agents**: Autonomous reasoning with tool usage for complex queries
- **Responsive UI**: Mobile, tablet, and desktop layouts
- **Material UI**: Professional component library
- **Document Upload**: Upload and process legal documents

## Tech Stack

- **React 18**: Modern UI library
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool
- **Material UI (MUI)**: Component library
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **Recharts**: Data visualization

## Project Structure

```
src/
├── components/        # Reusable UI components
│   ├── Navbar.tsx
│   ├── SearchBar.tsx
│   ├── CaseCard.tsx
│   ├── ResultsList.tsx
│   └── AIResults.tsx
├── pages/            # Page components
│   ├── SearchPage.tsx
│   ├── CaseDetailPage.tsx
│   └── UploadPage.tsx
├── hooks/            # Custom React hooks
│   ├── useSearch.ts
│   ├── useDocuments.ts
│   └── useCaseDetail.ts
├── services/         # API client and services
│   ├── apiClient.ts
│   ├── searchService.ts
│   └── caseService.ts
├── types/            # TypeScript types
│   └── models.ts
├── utils/            # Utility functions
│   ├── constants.ts
│   └── formatting.ts
├── App.tsx          # Main app component with routing
├── main.tsx         # Entry point
└── index.css        # Global styles
```

## Setup Instructions

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Configure API endpoint in `.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

Build for production:
```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

### Type Checking

Check TypeScript types without building:
```bash
npm run type-check
```

### Linting

Run ESLint:
```bash
npm run lint
```

## Key Components

### SearchBar
- Switch between Standard, RAG, and Agent search modes
- Real-time query input with helpful hints
- Visual loading state

### CaseCard
- Display case metadata (title, year, judge, decision)
- Relevance score with progress bar
- Link to case details

### ResultsList
- Paginated results display
- Shows total results and current query
- Error handling

### AIResults
- RAG result display with sources
- Agent reasoning trace with accordion panels
- Source citations

## API Integration

The frontend communicates with the backend API at the configured `VITE_API_BASE_URL`:

- `POST /api/search` - Standard vector search
- `POST /api/rag-query` - RAG-powered search
- `POST /api/agent-query` - Agent-powered query
- `GET /api/cases/{caseId}` - Case details
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - List documents
- `DELETE /api/documents/{docId}` - Delete document

## State Management

Uses React Context API for global state:

- **SearchContext**: Search results, query state, loading/error
- **Custom Hooks**: useSearch, useDocuments, useCaseDetail

## Styling

Material UI theming with custom configuration:
- Primary color: #1976d2
- Responsive breakpoints: mobile, tablet, desktop
- Dark and light theme support

## Performance

- Code splitting with lazy routes
- Optimized images and assets
- Efficient re-renders with proper hooks usage
- API request debouncing

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### API Connection Issues
- Verify backend is running at `VITE_API_BASE_URL`
- Check CORS settings in backend
- Inspect browser console for network errors

### Build Issues
- Clear `node_modules` and `package-lock.json`, then reinstall
- Clear `.vite` cache
- Ensure Node.js version matches requirements

### Type Errors
- Run `npm run type-check` to verify TypeScript
- Ensure all imports use correct paths with path aliases

## Development Tips

- Use React DevTools extension for debugging
- Enable Network tab to inspect API calls
- Use localStorage for persisting user preferences
- Component reusability is key for maintainability

## Future Enhancements

- WebSocket support for real-time updates
- Advanced filtering and faceted search
- User authentication and sessions
- Saved searches and case bookmarks
- Export results to PDF/CSV
- Dark mode theme
- Multi-language support
