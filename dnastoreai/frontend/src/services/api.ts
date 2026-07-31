import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({ baseURL: API_BASE });

export interface PipelineConfig {
  compression: string;
  encoding: string;
  ecc: string;
  block_size: number;
  optimize: boolean;
  substitution_rate: number;
  sequencing: string;
  coverage_depth: number;
}

export interface StoreResponse {
  archive_id: string;
  filename: string;
  original_size: number;
  compressed_size: number;
  total_dna_length: number;
  num_blocks: number;
  compression_ratio: number;
  sequences: string[];
  metrics: Record<string, unknown>;
}

export interface ArchiveItem {
  id: string;
  filename: string;
  file_type: string;
  original_size: number;
  total_dna_length: number;
  num_blocks: number;
  encoding: string;
  created_at: string;
}

export async function storeFile(file: File, config?: Partial<PipelineConfig>): Promise<StoreResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const params = new URLSearchParams(config as Record<string, string>);
  const { data } = await api.post<StoreResponse>(`/store?${params}`, formData);
  return data;
}

export async function retrieveFile(archiveId: string, config?: Partial<PipelineConfig>) {
  const { data } = await api.post('/retrieve', { archive_id: archiveId, config: config || {} });
  return data;
}

export async function simulateArchive(archiveId: string, config?: Partial<PipelineConfig>) {
  const { data } = await api.post('/simulate', { archive_id: archiveId, config: config || {} });
  return data;
}

export async function runExperiment(params: Record<string, unknown>) {
  const { data } = await api.post('/experiment', params);
  return data;
}

export async function getMetrics() {
  const { data } = await api.get('/metrics');
  return data;
}

export async function listArchives(): Promise<ArchiveItem[]> {
  const { data } = await api.get<ArchiveItem[]>('/archive');
  return data;
}

export async function getDna(archiveId: string, blockIndex = 0) {
  const { data } = await api.get(`/dna/${archiveId}?block_index=${blockIndex}`);
  return data;
}

export default api;
