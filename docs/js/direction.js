/** PM Direction panel: latest challenge, plan, summary */

class DirectionPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.data = null;
        this._setupTabs();
    }

    _setupTabs() {
        const tabs = document.querySelectorAll('.sidebar-tabs .tab-btn');
        const panels = document.querySelectorAll('#sidebar .tab-panel');
        tabs.forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.getAttribute('data-tab');
                tabs.forEach(b => b.classList.remove('active'));
                panels.forEach(p => p.classList.remove('active'));
                btn.classList.add('active');
                const entityDetails = document.getElementById('entity-details');
                if (entityDetails) entityDetails.style.display = 'none';
                const panel = tab === 'news' ? document.getElementById('news-panel') : document.getElementById('direction-panel');
                if (panel) panel.classList.add('active');
            });
        });
    }

    update(directionData) {
        if (!directionData) return;
        this.data = directionData;
        this.render();
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = '';

        const latest = this.data && this.data.latest;
        const history = (this.data && this.data.history) || [];

        // Evolution history panel (last evolutions)
        if (history.length > 0 || latest) {
            const historySection = document.createElement('div');
            historySection.className = 'evolution-history';
            const historyTitle = document.createElement('div');
            historyTitle.className = 'direction-label';
            historyTitle.textContent = 'Evolution history';
            historySection.appendChild(historyTitle);
            const entries = latest ? [...history, latest] : history;
            const lastN = entries.slice(-5).reverse();
            lastN.forEach(entry => {
                const line = document.createElement('p');
                line.className = 'evolution-entry';
                line.textContent = (entry.summary || entry.challenge || '').substring(0, 120) + (entry.summary && entry.summary.length > 120 ? '…' : '');
                if (entry.timestamp) {
                    const ts = document.createElement('span');
                    ts.className = 'evolution-timestamp';
                    ts.textContent = ' ' + new Date(entry.timestamp).toLocaleString();
                    line.appendChild(ts);
                }
                historySection.appendChild(line);
            });
            this.container.appendChild(historySection);
        }

        if (!latest || !latest.challenge) {
            if (!history.length) {
                this.container.innerHTML = '<p style="color: #888;">No direction set yet. Run a cycle to see the Planner\'s challenge and plan.</p>';
            }
            return;
        }

        const currentLabel = document.createElement('div');
        currentLabel.className = 'direction-label';
        currentLabel.textContent = 'Current direction';
        this.container.appendChild(currentLabel);

        const summaryEl = document.createElement('p');
        summaryEl.className = 'direction-summary';
        summaryEl.textContent = latest.summary || latest.challenge.split('.')[0] + '.';
        this.container.appendChild(summaryEl);

        const challengeLabel = document.createElement('div');
        challengeLabel.className = 'direction-label';
        challengeLabel.textContent = 'Challenge';
        this.container.appendChild(challengeLabel);
        const challengeEl = document.createElement('p');
        challengeEl.className = 'direction-challenge';
        challengeEl.textContent = latest.challenge;
        this.container.appendChild(challengeEl);

        const planLabel = document.createElement('div');
        planLabel.className = 'direction-label';
        planLabel.textContent = 'Plan';
        this.container.appendChild(planLabel);
        const planEl = document.createElement('pre');
        planEl.className = 'direction-plan';
        planEl.textContent = latest.plan || '-';
        this.container.appendChild(planEl);

        const hintEl = document.createElement('div');
        hintEl.className = 'direction-hint';
        hintEl.textContent = 'Focus: ' + (latest.implementation_hint || 'general');
        this.container.appendChild(hintEl);

        if (latest.timestamp) {
            const ts = document.createElement('div');
            ts.className = 'direction-timestamp';
            ts.textContent = new Date(latest.timestamp).toLocaleString();
            this.container.appendChild(ts);
        }
    }
}

const directionPanel = new DirectionPanel('direction-content');
window.directionPanel = directionPanel;
