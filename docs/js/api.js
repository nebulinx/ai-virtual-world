/** API client for fetching world state and news from GitHub raw URLs */

const GITHUB_RAW_BASE = "https://raw.githubusercontent.com/nebulinx/ai-virtual-world/main";
const WORLD_JSON_URL = `${GITHUB_RAW_BASE}/backend/data/world.json`;
const NEWS_JSON_URL = `${GITHUB_RAW_BASE}/backend/data/news.json`;
const DIRECTION_JSON_URL = `${GITHUB_RAW_BASE}/backend/data/direction.json`;
const POLL_INTERVAL = 30000; // 30 seconds

class API {
    constructor() {
        this.cache = {
            world: null,
            news: null,
            direction: null,
            lastFetch: {
                world: 0,
                news: 0,
                direction: 0
            }
        };
    }

    async fetchWorld() {
        const now = Date.now();
        // Use cache if less than 10 seconds old
        if (this.cache.world && (now - this.cache.lastFetch.world) < 10000) {
            return this.cache.world;
        }

        try {
            const response = await fetch(WORLD_JSON_URL + `?t=${now}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            this.cache.world = data;
            this.cache.lastFetch.world = now;
            return data;
        } catch (error) {
            console.error("Failed to fetch world:", error);
            // Return cached data on error
            return this.cache.world;
        }
    }

    async fetchNews() {
        const now = Date.now();
        // Use cache if less than 10 seconds old
        if (this.cache.news && (now - this.cache.lastFetch.news) < 10000) {
            return this.cache.news;
        }

        try {
            const response = await fetch(NEWS_JSON_URL + `?t=${now}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            this.cache.news = data;
            this.cache.lastFetch.news = now;
            return data;
        } catch (error) {
            console.error("Failed to fetch news:", error);
            // Return cached data on error
            return this.cache.news;
        }
    }

    async fetchDirection() {
        const now = Date.now();
        if (this.cache.direction && (now - this.cache.lastFetch.direction) < 10000) {
            return this.cache.direction;
        }
        try {
            const response = await fetch(DIRECTION_JSON_URL + `?t=${now}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            this.cache.direction = data;
            this.cache.lastFetch.direction = now;
            return data;
        } catch (error) {
            console.error("Failed to fetch direction:", error);
            return this.cache.direction;
        }
    }

    startPolling(onWorldUpdate, onNewsUpdate, onDirectionUpdate) {
        // Initial fetch
        this.fetchWorld().then(onWorldUpdate);
        this.fetchNews().then(onNewsUpdate);
        if (onDirectionUpdate) this.fetchDirection().then(onDirectionUpdate);

        // Poll periodically
        setInterval(() => {
            this.fetchWorld().then(onWorldUpdate);
            this.fetchNews().then(onNewsUpdate);
            if (onDirectionUpdate) this.fetchDirection().then(onDirectionUpdate);
        }, POLL_INTERVAL);
    }
}

const api = new API();
