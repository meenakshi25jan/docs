import { ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box, Drawer, List, ListItemButton, ListItemIcon, ListItemText,
  Typography, AppBar, Toolbar,
} from '@mui/material';
import StorageIcon from '@mui/icons-material/Storage';
import UploadIcon from '@mui/icons-material/Upload';
import ScienceIcon from '@mui/icons-material/Science';
import RestoreIcon from '@mui/icons-material/Restore';
import BiotechIcon from '@mui/icons-material/Biotech';
import BarChartIcon from '@mui/icons-material/BarChart';
import DashboardIcon from '@mui/icons-material/Dashboard';

const DRAWER_WIDTH = 260;

const navItems = [
  { label: 'Dashboard', path: '/', icon: <DashboardIcon /> },
  { label: 'Encode & Store', path: '/encode', icon: <UploadIcon /> },
  { label: 'Simulate', path: '/simulate', icon: <ScienceIcon /> },
  { label: 'Recover', path: '/recover', icon: <RestoreIcon /> },
  { label: 'Experiments', path: '/experiments', icon: <BiotechIcon /> },
  { label: 'Analytics', path: '/analytics', icon: <BarChartIcon /> },
];

export default function Layout({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (t) => t.zIndex.drawer + 1, bgcolor: '#0d1230' }}>
        <Toolbar>
          <StorageIcon sx={{ mr: 2, color: '#4fc3f7' }} />
          <Typography variant="h6" noWrap sx={{ fontWeight: 700 }}>
            DNAStoreAI
          </Typography>
          <Typography variant="body2" sx={{ ml: 2, opacity: 0.6 }}>
            DNA Data Storage Research Platform
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': { width: DRAWER_WIDTH, bgcolor: '#0d1230', borderRight: '1px solid #1e2a5a' },
        }}
      >
        <Toolbar />
        <List>
          {navItems.map((item) => (
            <ListItemButton
              key={item.path}
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{ '&.Mui-selected': { bgcolor: 'rgba(79,195,247,0.12)', borderRight: '3px solid #4fc3f7' } }}
            >
              <ListItemIcon sx={{ color: location.pathname === item.path ? '#4fc3f7' : 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, ml: `${DRAWER_WIDTH}px`, mt: 8, minHeight: '100vh' }}>
        {children}
      </Box>
    </Box>
  );
}
