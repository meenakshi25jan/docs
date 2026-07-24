import { useEffect, useState } from 'react';
import {
  Box, Typography, Card, CardContent, FormControl, InputLabel,
  Select, MenuItem, Button, Grid,
} from '@mui/material';
import { listArchives, simulateArchive, ArchiveItem } from '../services/api';

export default function SimulatePage() {
  const [archives, setArchives] = useState<ArchiveItem[]>([]);
  const [selected, setSelected] = useState('');
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { listArchives().then(setArchives).catch(() => {}); }, []);

  const handleSimulate = async () => {
    if (!selected) return;
    setLoading(true);
    try {
      const res = await simulateArchive(selected, { sequencing: 'illumina', coverage_depth: 30 });
      setResult(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={700}>Simulate Storage</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Simulate DNA synthesis, degradation, and sequencing
      </Typography>

      <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a', mb: 3 }}>
        <CardContent>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Archive</InputLabel>
            <Select value={selected} label="Archive" onChange={(e) => setSelected(e.target.value)}>
              {archives.map((a) => <MenuItem key={a.id} value={a.id}>{a.filename}</MenuItem>)}
            </Select>
          </FormControl>
          <Button variant="contained" onClick={handleSimulate} disabled={!selected || loading}>
            Run Simulation
          </Button>
        </CardContent>
      </Card>

      {result && (
        <Grid container spacing={3}>
          {['synthesis_stats', 'degradation_stats', 'sequencing_stats'].map((key) => (
            <Grid item xs={12} md={4} key={key}>
              <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ textTransform: 'capitalize' }}>
                    {key.replace('_stats', '')}
                  </Typography>
                  <pre style={{ fontSize: 12, overflow: 'auto' }}>
                    {JSON.stringify(result[key], null, 2)}
                  </pre>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
