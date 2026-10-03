import { PRContext, ScanResult } from '../lib/types';

export async function renderPanel(container: HTMLElement, context: PRContext) {
    container.className = 'codefort-panel bg-gray-900 text-gray-100 shadow-lg font-sans';
    
    container.innerHTML = `
        <div class="p-16 border-b border-gray-800 flex justify-between items-center">
            <h2 class="text-lg font-semibold">CodeFort Guard</h2>
            <button id="cf-close-btn" class="text-gray-400 hover:text-white">&times;</button>
        </div>
        <div class="p-16" id="cf-content">
            <div class="animate-pulse text-gray-400">Loading scan results...</div>
        </div>
    `;

    document.getElementById('cf-close-btn')?.addEventListener('click', () => {
        container.remove();
    });

    try {
        // Send message to background script to fetch data
        chrome.runtime.sendMessage(
            { action: 'FETCH_SCAN', context },
            (response: { success: boolean; data?: ScanResult; error?: string }) => {
                const contentDiv = document.getElementById('cf-content');
                if (!contentDiv) return;

                if (!response || !response.success || !response.data) {
                    contentDiv.innerHTML = `<div class="text-severity-low">Unable to connect to CodeFort. Check your connection.</div>`;
                    return;
                }

                const data = response.data;
                
                if (data.findings_count === 0) {
                    contentDiv.innerHTML = `<div class="text-severity-info">No security findings were detected in this scan.</div>`;
                    return;
                }

                contentDiv.innerHTML = `
                    <div class="mb-16">
                        <div class="text-sm uppercase text-gray-400">Status</div>
                        <div class="text-xl font-bold">${data.policy_result?.decision || 'REVIEW'}</div>
                    </div>
                    <div class="mb-16">
                        <details class="bg-gray-800 rounded p-8">
                            <summary class="cursor-pointer font-semibold">Why Flagged? (${data.findings_count} findings)</summary>
                            <div class="mt-8 text-sm space-y-8">
                                <!-- Placeholder for findings list -->
                                <div class="font-mono text-xs text-severity-high">workflow.untrusted_checkout</div>
                            </div>
                        </details>
                    </div>
                    <div class="mt-24 pt-16 border-t border-gray-800 text-xs text-gray-400 text-center">
                        <a href="http://localhost:3000/scans/${data.scan_id}" target="_blank" class="hover:text-white underline">Open in CodeFort Dashboard</a>
                    </div>
                `;
            }
        );
    } catch (e) {
        console.error(e);
    }
}
