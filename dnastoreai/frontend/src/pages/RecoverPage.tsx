import { useEffect, useState } from 'react';
import {
  Box, Typography, Card, CardContent, FormControl, InputLabel,
  Select, MenuItem, Button, Alert, Grid,
} from '@mui/material';
import { listArchives, retrieveFile, ArchiveItem } from '../services/api';

export default function RecoverPage() {
  const [archives, setArchives] = useState<ArchiveItem[]>([]);
  const [selected, setSelected] = useState('');
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { listArchives().then(setArchives).catch(() => {}); }, []);

  const handleRecover = async () => {
    if (!selected) return;
    setLoading(true);
    try {
      const res = await retrieveFile(selected);
      setResult(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={700}>Recover Data</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Reconstruct original files from DNA archives
      </Typography>

      <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a', mb: 3 }}>
        <CardContent>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Archive</InputLabel>
            <Select value={selected} label="Archive" onChange={(e) => setSelected(e.target.value)}>
              {archives.map((a) => <MenuItem key={a.id} value={a.id}>{a.filename}</MenuItem>)}
            </Select>
          </FormControl>
          <Button variant="contained" onClick={handleRecover} disabled={!selected || loading}>
            Recover File
          </Button>
        </CardContent>
      </Card>

      {result && (
        <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a' }}>
          <CardContent>
            <Alert severity={result.checksum_valid ? 'success' : 'warning'} sx={{ mb: 2 }}>
              Checksum {result.checksum_valid ? 'Valid' : 'Invalid'}
            </Alert>
            <Grid container spacing={2}>
              <Grid item xs={6}><Typography>Filename: {String(result.filename)}</Typography></Grid>
              <Grid item xs={6}><Typography>Recovered Size: {String(result.recovered_size)} bytes</Typography></Grid>
            </Grid>
            <pre style={{ fontSize: 12, marginTop: 16 }}>
              {JSON.stringify(result.metrics, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
