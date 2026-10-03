import { PRContext } from '../lib/types';
import { renderPanel } from './panel';

function extractPRContext(url: string): PRContext | null {
    const match = url.match(/github\.com\/([^\/]+)\/([^\/]+)\/pull\/(\d+)/);
    if (match) {
        return {
            owner: match[1],
            repo: match[2],
            prNumber: parseInt(match[3], 10)
        };
    }
    return null;
}

function injectButton(context: PRContext) {
    try {
        const existingBtn = document.getElementById('codefort-guard-btn');
        if (existingBtn) return;

        const headerActions = document.querySelector('.gh-header-actions');
        if (!headerActions) return;

        const btn = document.createElement('button');
        btn.id = 'codefort-guard-btn';
        btn.className = 'btn btn-sm';
        btn.innerText = '🛡️ CodeFort Guard';
        btn.onclick = () => togglePanel(context);

        headerActions.prepend(btn);
    } catch (e) {
        console.error('CodeFort Guard: Error injecting button', e);
    }
}

function togglePanel(context: PRContext) {
    try {
        let panel = document.getElementById('codefort-guard-panel');
        if (panel) {
            panel.remove();
        } else {
            panel = document.createElement('div');
            panel.id = 'codefort-guard-panel';
            document.body.appendChild(panel);
            renderPanel(panel, context);
        }
    } catch (e) {
        console.error('CodeFort Guard: Error toggling panel', e);
    }
}

function init() {
    const context = extractPRContext(window.location.href);
    if (context) {
        injectButton(context);
    }
}

// GitHub uses Turbo/pjax for navigation
document.addEventListener('pjax:end', init);
document.addEventListener('turbo:load', init);

init();
