import { request } from './client';
import type { HealthResponse, AnalyzeResponse, AnalyzeRequest } from '../types/contract';

export async function checkHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/api/health');
}

export async function analyzeRepository(repoUrl: string, signal?: AbortSignal): Promise<AnalyzeResponse> {
  const payload: AnalyzeRequest = { url: repoUrl };
  return request<AnalyzeResponse>('/api/analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
    signal,
  });
}
