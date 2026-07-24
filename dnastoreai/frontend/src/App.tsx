import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import EncodePage from './pages/EncodePage';
import SimulatePage from './pages/SimulatePage';
import RecoverPage from './pages/RecoverPage';
import ExperimentsPage from './pages/ExperimentsPage';
import AnalyticsPage from './pages/AnalyticsPage';

export default function App() {
  return (
    <Layout>
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/encode" element={<EncodePage />} />
          <Route path="/simulate" element={<SimulatePage />} />
          <Route path="/recover" element={<RecoverPage />} />
          <Route path="/experiments" element={<ExperimentsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
        </Routes>
      </Box>
    </Layout>
  );
}
