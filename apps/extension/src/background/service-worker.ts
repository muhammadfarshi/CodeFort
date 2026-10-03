import { fetchScanResult } from '../lib/api';

// Cache scan results briefly to avoid redundant calls
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 60000; // 1 minute

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'FETCH_SCAN' && message.context) {
        const key = `${message.context.owner}/${message.context.repo}/${message.context.prNumber}`;
        const cached = cache.get(key);

        if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
            sendResponse({ success: true, data: cached.data });
            return true;
        }

        fetchScanResult(message.context)
            .then(data => {
                if (data) {
                    cache.set(key, { data, timestamp: Date.now() });
                    sendResponse({ success: true, data });
                } else {
                    sendResponse({ success: false, error: 'Not found' });
                }
            })
            .catch(error => {
                console.error(error);
                sendResponse({ success: false, error: error.message });
            });
        
        return true; // Keep message channel open for async response
    }
});
