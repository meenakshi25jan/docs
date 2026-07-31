import { useState } from 'react';
import {
  Box, Typography, Card, CardContent, Button, Grid, FormControl,
  InputLabel, Select, MenuItem, TextField, Alert, LinearProgress,
} from '@mui/material';
import { runExperiment } from '../services/api';

export default function ExperimentsPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [config, setConfig] = useState({
    name: 'benchmark',
    dataset_type: 'mixed',
    file_count: 5,
    encoding: 'gc_balanced',
    ecc: 'reed_solomon',
    sequencing: 'illumina',
  });

  const handleRun = async () => {
    setLoading(true);
    try {
      const res = await runExperiment(config);
      setResult(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={700}>Research Experiments</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Run benchmark experiments across encoding, ECC, and sequencing configurations
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a' }}>
            <CardContent>
              <TextField fullWidth label="Experiment Name" value={config.name}
                onChange={(e) => setConfig({ ...config, name: e.target.value })} sx={{ mb: 2 }} />
              <TextField fullWidth label="File Count" type="number" value={config.file_count}
                onChange={(e) => setConfig({ ...config, file_count: Number(e.target.value) })} sx={{ mb: 2 }} />
              {(['dataset_type', 'encoding', 'ecc', 'sequencing'] as const).map((key) => (
                <FormControl fullWidth sx={{ mb: 2 }} key={key}>
                  <InputLabel>{key}</InputLabel>
                  <Select value={config[key]} label={key}
                    onChange={(e) => setConfig({ ...config, [key]: e.target.value })}>
                    {key === 'dataset_type' && ['text', 'image', 'binary', 'mixed'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                    {key === 'encoding' && ['basic', 'rotating', 'gc_balanced'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                    {key === 'ecc' && ['reed_solomon', 'bch', 'ldpc', 'fountain'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                    {key === 'sequencing' && ['illumina', 'nanopore', 'pacbio'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                  </Select>
                </FormControl>
              ))}
              <Button variant="contained" fullWidth onClick={handleRun} disabled={loading}>
                Run Experiment
              </Button>
              {loading && <LinearProgress sx={{ mt: 2 }} />}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          {result && (
            <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a' }}>
              <CardContent>
                <Alert severity="success" sx={{ mb: 2 }}>Experiment {String(result.experiment_id)}</Alert>
                <Typography variant="h6">Summary</Typography>
                <pre style={{ fontSize: 12 }}>{JSON.stringify(result.summary, null, 2)}</pre>
                <Typography variant="h6" sx={{ mt: 2 }}>File Results</Typography>
                <pre style={{ fontSize: 11, maxHeight: 400, overflow: 'auto' }}>
                  {JSON.stringify(result.file_results, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
