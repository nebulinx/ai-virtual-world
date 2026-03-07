/** News feed display and management */

class NewsFeed {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.newsItems = [];
    }

    update(newsData) {
        if (!newsData || !newsData.latest) return;
        
        this.newsItems = newsData.latest.slice(-10).reverse(); // Show last 10, newest first
        this.render();
    }

    render() {
        this.container.innerHTML = '';
        
        if (this.newsItems.length === 0) {
            this.container.innerHTML = '<p style="color: #888;">No news yet...</p>';
            return;
        }

        this.newsItems.forEach(item => {
            const newsElement = document.createElement('div');
            newsElement.className = 'news-item';
            
            const headline = document.createElement('h3');
            headline.textContent = item.headline || 'World Update';
            
            const body = document.createElement('p');
            body.textContent = item.body || 'No description available.';
            
            const timestamp = document.createElement('div');
            timestamp.className = 'timestamp';
            if (item.timestamp) {
                const date = new Date(item.timestamp);
                timestamp.textContent = date.toLocaleString();
            }
            
            newsElement.appendChild(headline);
            newsElement.appendChild(body);
            newsElement.appendChild(timestamp);
            
            this.container.appendChild(newsElement);
        });

        // Auto-scroll to top (newest)
        this.container.scrollTop = 0;
    }
}

const newsFeed = new NewsFeed('news-feed');
