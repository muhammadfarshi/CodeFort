import { PRContext, ScanResult } from './types';

const API_BASE_URL = 'http://localhost:8000';

export async function fetchScanResult(context: PRContext): Promise<ScanResult | null> {
    const { owner, repo, prNumber } = context;
    try {
        const url = `${API_BASE_URL}/api/v1/scans/${owner}/${repo}/pr/${prNumber}`;
        const response = await fetch(url, {
            credentials: 'omit', // No active auth integration yet
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            console.error(`CodeFort API error: ${response.status} ${response.statusText}`);
            return null;
        }

        const data: ScanResult = await response.json();
        return data;
    } catch (error) {
        console.error('CodeFort API fetch failed:', error);
        return null;
    }
}
