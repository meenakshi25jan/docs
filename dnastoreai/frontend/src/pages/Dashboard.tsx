import { useEffect, useState } from 'react';
import { Grid, Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { listArchives, getMetrics } from '../services/api';

export default function Dashboard() {
  const [archives, setArchives] = useState<unknown[]>([]);
  const [metrics, setMetrics] = useState<Record<string, Record<string, number>>>({});

  useEffect(() => {
    listArchives().then(setArchives).catch(() => setArchives([]));
    getMetrics().then(setMetrics).catch(() => setMetrics({}));
  }, []);

  const stats = [
    { label: 'Archives', value: archives.length, color: '#4fc3f7' },
    { label: 'DNA Bases', value: metrics.storage?.dna_length || 0, color: '#81c784' },
    { label: 'Logical Size', value: `${((metrics.storage?.logical_size || 0) / 1024).toFixed(1)} KB`, color: '#ffb74d' },
    { label: 'Density', value: (metrics.storage?.density || 0).toFixed(2), color: '#ce93d8' },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={700}>Research Dashboard</Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        AI-Assisted DNA Data Storage and Retrieval Platform
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((s) => (
          <Grid item xs={12} sm={6} md={3} key={s.label}>
            <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary">{s.label}</Typography>
                <Typography variant="h4" sx={{ color: s.color, fontWeight: 700 }}>{s.value}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a', mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Pipeline Overview</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
            {['File Input', 'Compression', 'Segmentation', 'ECC', 'DNA Encode', 'Optimization',
              'Synthesis', 'Archive', 'Degradation', 'Sequencing', 'Reconstruction'].map((step, i) => (
              <Box key={step} sx={{ display: 'flex', alignItems: 'center' }}>
                <Chip label={step} size="small" sx={{ bgcolor: '#1e2a5a' }} />
                {i < 10 && <Typography sx={{ mx: 0.5, opacity: 0.4 }}>→</Typography>}
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Recent Archives</Typography>
          {archives.length === 0 ? (
            <Typography color="text.secondary">No archives yet. Upload a file to get started.</Typography>
          ) : (
            (archives as { id: string; filename: string; original_size: number; encoding: string }[]).map((a) => (
              <Box key={a.id} sx={{ py: 1, borderBottom: '1px solid #1e2a5a' }}>
                <Typography>{a.filename}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {a.original_size} bytes · {a.encoding}
                </Typography>
              </Box>
            ))
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
