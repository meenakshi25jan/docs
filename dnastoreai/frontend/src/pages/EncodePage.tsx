import { useState } from 'react';
import {
  Box, Typography, Button, Card, CardContent, FormControl, InputLabel,
  Select, MenuItem, Grid, Alert, LinearProgress, TextField,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { storeFile, StoreResponse } from '../services/api';

export default function EncodePage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<StoreResponse | null>(null);
  const [error, setError] = useState('');
  const [config, setConfig] = useState({
    compression: 'gzip',
    encoding: 'gc_balanced',
    ecc: 'reed_solomon',
    block_size: 4096,
  });

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const res = await storeFile(file, config);
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={700}>Encode & Store</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Upload a file to encode into DNA sequences with error correction
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Configuration</Typography>
              {(['compression', 'encoding', 'ecc'] as const).map((key) => (
                <FormControl fullWidth sx={{ mb: 2 }} key={key}>
                  <InputLabel>{key}</InputLabel>
                  <Select
                    value={config[key]}
                    label={key}
                    onChange={(e) => setConfig({ ...config, [key]: e.target.value })}
                  >
                    {key === 'compression' && ['gzip', 'zlib', 'lzma'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                    {key === 'encoding' && ['basic', 'rotating', 'gc_balanced', 'custom'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                    {key === 'ecc' && ['reed_solomon', 'bch', 'ldpc', 'fountain'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                  </Select>
                </FormControl>
              ))}
              <TextField
                fullWidth label="Block Size" type="number" value={config.block_size}
                onChange={(e) => setConfig({ ...config, block_size: Number(e.target.value) })}
                sx={{ mb: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card sx={{ bgcolor: '#121836', border: '1px solid #1e2a5a' }}>
            <CardContent>
              <Button variant="outlined" component="label" startIcon={<UploadFileIcon />} sx={{ mb: 2 }}>
                Select File
                <input type="file" hidden onChange={(e) => setFile(e.target.files?.[0] || null)} />
              </Button>
              {file && <Typography sx={{ mb: 2 }}>{file.name} ({file.size} bytes)</Typography>}
              <Button variant="contained" onClick={handleUpload} disabled={!file || loading} fullWidth>
                Encode to DNA
              </Button>
              {loading && <LinearProgress sx={{ mt: 2 }} />}
              {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
              {result && (
                <Box sx={{ mt: 3 }}>
                  <Alert severity="success">Archive ID: {result.archive_id}</Alert>
                  <Grid container spacing={2} sx={{ mt: 1 }}>
                    <Grid item xs={6}><Typography variant="body2">DNA Length: {result.total_dna_length}</Typography></Grid>
                    <Grid item xs={6}><Typography variant="body2">Blocks: {result.num_blocks}</Typography></Grid>
                    <Grid item xs={6}><Typography variant="body2">Compression: {result.compression_ratio.toFixed(2)}x</Typography></Grid>
                    <Grid item xs={6}><Typography variant="body2">Compressed: {result.compressed_size} bytes</Typography></Grid>
                  </Grid>
                  {result.sequences[0] && (
                    <Box sx={{ mt: 2, p: 2, bgcolor: '#0a0e27', borderRadius: 1, fontFamily: 'monospace', fontSize: 12, overflow: 'auto', maxHeight: 120 }}>
                      {result.sequences[0].slice(0, 200)}...
                    </Box>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
