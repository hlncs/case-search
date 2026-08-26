import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box } from '@mui/material';
import { SearchProvider } from '@hooks/useSearch';
import Navbar from '@components/Navbar';
import { SearchPage, CaseDetailPage, UploadPage } from '@pages/index';

// Create MUI theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#424242',
      light: '#757575',
      dark: '#212121',
    },
    background: {
      default: '#fafafa',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1.1rem',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

/**
 * Main App component with routing
 */
const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <SearchProvider>
          <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
            <Navbar />
            <Box component="main" sx={{ flexGrow: 1, backgroundColor: '#fafafa' }}>
              <Routes>
                <Route path="/" element={<SearchPage />} />
                <Route path="/cases/:caseId" element={<CaseDetailPage />} />
                <Route path="/upload" element={<UploadPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Box>
          </Box>
        </SearchProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;
