import { useEffect, useState } from 'react';
import { Box, Typography, Card, CardContent, Grid } from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line,
} from 'recharts';
import { getMetrics, listArchives } from '../services/api';

const COLORS = ['#4fc3f7', '#81c784', '#ffb74d', '#ce93d8', '#ef5350'];

export default function AnalyticsPage() {
  const [metrics, setMetrics] = useState<Record<string, Record<string, number>>>({});
  const [archives, setArchives] = useState<{ filename: string; original_size: number; total_dna_length: number }[]>([]);

  useEffect(() => {
    getMetrics().then(setMetrics).catch(() => {});
    listArchives().then(setArchives).catch(() => {});
  }, []);

  const storageData = [
    { name: 'Logical', value: metrics.storage?.logical_size || 0 },
    { name: 'Physical', value: metrics.storage?.physical_size || 0 },
    { name: 'DNA', value: metrics.storage?.dna_length || 0 },
  ];

  const archiveChart = archives.map((a) => ({
    name: a.filename.slice(0, 15),
    size: a.original_size,
    dna: a.total_dna_length,
  }));

  const bioData = [
    { metric: 'GC Content', value: (metrics.biological?.gc_content || 0) * 100 },
    { metric: 'Fitness', value: (metrics.biological?.fitness_score || 0) * 100 },
    { metric: 'Hairpin Risk', value: (metrics.biological?.hairpin_risk || 0) * 100 },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={700}>Visual Analytics</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Storage density, biological metrics, and recovery analytics
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Storage Distribution</Typography>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={storageData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}
                    label={({ name, value }) => `${name}: ${value}`}>
                    {storageData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Biological Metrics</Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={bioData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2a5a" />
                  <XAxis dataKey="metric" stroke="#888" />
                  <YAxis stroke="#888" />
                  <Tooltip />
                  <Bar dataKey="value" fill="#4fc3f7" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Archive Size vs DNA Length</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={archiveChart}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2a5a" />
                  <XAxis dataKey="name" stroke="#888" />
                  <YAxis stroke="#888" />
                  <Tooltip />
                  <Line type="monotone" dataKey="size" stroke="#4fc3f7" name="File Size" />
                  <Line type="monotone" dataKey="dna" stroke="#81c784" name="DNA Length" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
