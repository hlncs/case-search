import React from 'react';
import { AppBar, Toolbar, Typography, Box, Button, Container } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import SearchIcon from '@mui/icons-material/Search';

/**
 * Navigation bar component
 */
const Navbar: React.FC = () => {
  return (
    <AppBar position="sticky" elevation={1}>
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          <SearchIcon sx={{ mr: 2, fontSize: 28 }} />
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{
              flexGrow: 1,
              textDecoration: 'none',
              color: 'inherit',
              fontWeight: 600,
            }}
          >
            Legal Case Search
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              color="inherit"
              component={RouterLink}
              to="/"
              sx={{
                textTransform: 'none',
                fontSize: '0.95rem',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                },
              }}
            >
              Search
            </Button>
            <Button
              color="inherit"
              component={RouterLink}
              to="/upload"
              sx={{
                textTransform: 'none',
                fontSize: '0.95rem',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                },
              }}
            >
              Upload
            </Button>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navbar;
