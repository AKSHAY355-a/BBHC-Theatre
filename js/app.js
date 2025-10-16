// BBHC Theater - Main Application Script
// Handles UI interactions, content filtering, search, and video playback

class BBHCTheater {
    constructor() {
        this.allContent = [];
        this.filteredContent = [];
        this.currentCategory = 'all';
        this.searchQuery = '';
        this.currentContentItem = null;
        
        this.init();
    }

    async init() {
        console.log('[BBHC] Initializing theater...');
        
        // Load content from database
        this.allContent = window.contentDatabase || [];
        this.filteredContent = [...this.allContent];
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Show skeleton loaders initially
        this.showSkeletonLoaders();
        
        // Simulate loading delay for smooth UX
        await this.delay(800);
        
        // Render initial content
        this.renderContent();
        
        console.log('[BBHC] ✓ Theater ready');
    }

    setupEventListeners() {
        // Sidebar toggle
        const hamburgerBtn = document.getElementById('hamburgerBtn');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');
        const closeSidebar = document.getElementById('closeSidebar');

        hamburgerBtn.addEventListener('click', () => this.toggleSidebar(true));
        closeSidebar.addEventListener('click', () => this.toggleSidebar(false));
        overlay.addEventListener('click', () => this.toggleSidebar(false));

        // Navigation links
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const filter = e.currentTarget.getAttribute('data-filter');
                this.applyFilter(filter);
                this.toggleSidebar(false);
                
                // Update active state
                navLinks.forEach(l => l.classList.remove('active'));
                e.currentTarget.classList.add('active');
            });
        });

        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');

        searchInput.addEventListener('input', (e) => {
            this.searchQuery = e.target.value.toLowerCase().trim();
            this.performSearch();
        });

        searchBtn.addEventListener('click', () => {
            searchInput.focus();
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });

        // Modal close handlers
        const modalClose = document.getElementById('modalClose');
        const modalOverlay = document.getElementById('modalOverlay');
        
        modalClose.addEventListener('click', () => this.closeDetailModal());
        modalOverlay.addEventListener('click', () => this.closeDetailModal());

        // Stream button
        const streamBtn = document.getElementById('streamBtn');
        streamBtn.addEventListener('click', () => this.startStreaming());

        // Player close handlers
        const playerClose = document.getElementById('playerClose');
        const playerOverlay = document.getElementById('playerOverlay');
        
        playerClose.addEventListener('click', () => this.closePlayer());
        playerOverlay.addEventListener('click', () => this.closePlayer());

        // Video player events
        const videoPlayer = document.getElementById('videoPlayer');
        videoPlayer.addEventListener('loadeddata', () => this.onVideoLoaded());
        videoPlayer.addEventListener('error', (e) => this.onVideoError(e));
    }

    toggleSidebar(show) {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');
        
        if (show) {
            sidebar.classList.add('active');
            overlay.classList.add('active');
        } else {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    }

    applyFilter(filter) {
        console.log(`[BBHC] Applying filter: ${filter}`);
        this.currentCategory = filter;
        
        // Show skeleton loaders
        this.showSkeletonLoaders();
        
        // Filter content based on category
        if (filter === 'all') {
            this.filteredContent = [...this.allContent];
            this.updateCategoryTitle('All Content');
        } else if (filter === 'movies') {
            this.filteredContent = this.allContent.filter(item => !item.is_series);
            this.updateCategoryTitle('Movies');
        } else if (filter === 'series') {
            this.filteredContent = this.allContent.filter(item => item.is_series);
            this.updateCategoryTitle('Series');
        } else if (filter.startsWith('genre-')) {
            const genre = filter.replace('genre-', '').replace('-', ' ');
            const genreCapitalized = genre.split(' ').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
            
            this.filteredContent = this.allContent.filter(item =>
                item.genre.some(g => g.toLowerCase() === genreCapitalized.toLowerCase())
            );
            this.updateCategoryTitle(genreCapitalized);
        } else if (filter.startsWith('year-')) {
            const year = parseInt(filter.replace('year-', ''));
            this.filteredContent = this.allContent.filter(item => item.year === year);
            this.updateCategoryTitle(year.toString());
        }
        
        // Apply search if active
        if (this.searchQuery) {
            this.performSearch();
        } else {
            // Simulate loading delay
            setTimeout(() => this.renderContent(), 500);
        }
    }

    performSearch() {
        console.log(`[BBHC] Searching: ${this.searchQuery}`);
        
        if (!this.searchQuery) {
            this.filteredContent = [...this.allContent];
            this.updateCategoryTitle('All Content');
            this.renderContent();
            return;
        }
        
        // Show skeleton loaders
        this.showSkeletonLoaders();
        
        // Search in title and description
        this.filteredContent = this.allContent.filter(item => {
            const matchesSearch = 
                item.title.toLowerCase().includes(this.searchQuery) ||
                item.description.toLowerCase().includes(this.searchQuery);
            
            // Also apply category filter if active
            let matchesCategory = true;
            if (this.currentCategory !== 'all') {
                if (this.currentCategory === 'movies') {
                    matchesCategory = !item.is_series;
                } else if (this.currentCategory === 'series') {
                    matchesCategory = item.is_series;
                } else if (this.currentCategory.startsWith('genre-')) {
                    const genre = this.currentCategory.replace('genre-', '').replace('-', ' ');
                    matchesCategory = item.genre.some(g => 
                        g.toLowerCase() === genre.toLowerCase()
                    );
                } else if (this.currentCategory.startsWith('year-')) {
                    const year = parseInt(this.currentCategory.replace('year-', ''));
                    matchesCategory = item.year === year;
                }
            }
            
            return matchesSearch && matchesCategory;
        });
        
        this.updateCategoryTitle(`Search: "${this.searchQuery}"`);
        
        // Simulate loading delay
        setTimeout(() => this.renderContent(), 400);
    }

    updateCategoryTitle(title) {
        const categoryTitle = document.getElementById('categoryTitle');
        categoryTitle.textContent = title;
    }

    showSkeletonLoaders() {
        const contentGrid = document.getElementById('contentGrid');
        const noResults = document.getElementById('noResults');
        
        noResults.style.display = 'none';
        
        // Create 12 skeleton cards
        const skeletonHTML = Array(12).fill().map(() => `
            <div class="skeleton-card">
                <div class="skeleton-poster"></div>
                <div class="skeleton-info">
                    <div class="skeleton-title"></div>
                    <div class="skeleton-meta"></div>
                </div>
            </div>
        `).join('');
        
        contentGrid.innerHTML = skeletonHTML;
    }

    renderContent() {
        const contentGrid = document.getElementById('contentGrid');
        const noResults = document.getElementById('noResults');
        
        // Check if no results
        if (this.filteredContent.length === 0) {
            contentGrid.innerHTML = '';
            noResults.style.display = 'block';
            return;
        }
        
        noResults.style.display = 'none';
        
        // Render content cards
        const cardsHTML = this.filteredContent.map(item => this.createContentCard(item)).join('');
        contentGrid.innerHTML = cardsHTML;
        
        // Add click handlers to cards
        document.querySelectorAll('.content-card').forEach(card => {
            card.addEventListener('click', () => {
                const contentId = card.getAttribute('data-id');
                this.showDetailModal(contentId);
            });
        });
        
        console.log(`[BBHC] Rendered ${this.filteredContent.length} items`);
    }

    createContentCard(item) {
        const genres = item.genre.slice(0, 2).map(g => 
            `<span class="genre-tag">${g}</span>`
        ).join('');
        
        const type = item.is_series ? 'Series' : 'Movie';
        
        return `
            <div class="content-card" data-id="${item.id}">
                <div class="card-poster">
                    <img src="${item.poster_url}" alt="${item.title}">
                    <div class="card-rating">
                        <i class="fas fa-star"></i>
                        <span>${item.imdb_rating}</span>
                    </div>
                </div>
                <div class="card-info">
                    <h3 class="card-title">${item.title}</h3>
                    <div class="card-meta">
                        <span>${item.year}</span>
                        <span>•</span>
                        <span>${type}</span>
                    </div>
                    <div class="card-genres">
                        ${genres}
                    </div>
                </div>
            </div>
        `;
    }

    showDetailModal(contentId) {
        const item = this.allContent.find(c => c.id === contentId);
        if (!item) return;
        
        this.currentContentItem = item;
        
        // Populate modal
        document.getElementById('modalPoster').src = item.poster_url;
        document.getElementById('modalTitle').textContent = item.title;
        document.getElementById('modalRating').textContent = item.imdb_rating;
        document.getElementById('modalYear').textContent = item.year;
        document.getElementById('modalType').textContent = item.is_series ? 'Series' : 'Movie';
        document.getElementById('modalDescription').textContent = item.description;
        document.getElementById('modalCast').textContent = item.cast.join(', ');
        
        // Render genres
        const genresHTML = item.genre.map(g => 
            `<span class="modal-genre-tag">${g}</span>`
        ).join('');
        document.getElementById('modalGenres').innerHTML = genresHTML;
        
        // Set IMDB link
        const imdbLink = document.getElementById('modalImdbLink');
        imdbLink.href = `https://www.imdb.com/title/${item.imdb_id}/`;
        
        // Show modal
        const modal = document.getElementById('detailModal');
        modal.classList.add('active');
        
        console.log(`[BBHC] Showing details for: ${item.title}`);
    }

    closeDetailModal() {
        const modal = document.getElementById('detailModal');
        modal.classList.remove('active');
    }

    async startStreaming() {
        if (!this.currentContentItem) return;
        
        console.log(`[BBHC] Starting stream: ${this.currentContentItem.title}`);
        
        // Close detail modal
        this.closeDetailModal();
        
        // Show player modal
        const playerModal = document.getElementById('playerModal');
        const playerTitle = document.getElementById('playerTitle');
        const playerLoading = document.getElementById('playerLoading');
        const videoPlayer = document.getElementById('videoPlayer');
        const videoSource = document.getElementById('videoSource');
        
        playerTitle.textContent = this.currentContentItem.title;
        playerModal.classList.add('active');
        playerLoading.classList.remove('hidden');
        videoPlayer.style.display = 'none';
        
        try {
            // Resolve streaming URL via Telegram
            const streamingUrl = await window.telegramLoader.resolveStreamingUrl(
                this.currentContentItem.id,
                this.currentContentItem
            );
            
            // Load video
            videoSource.src = streamingUrl;
            videoPlayer.load();
            
            console.log('[BBHC] ✓ Stream loaded successfully');
            
        } catch (error) {
            console.error('[BBHC] Stream loading failed:', error);
            this.handleStreamError(error);
        }
    }

    onVideoLoaded() {
        console.log('[BBHC] Video ready to play');
        
        const playerLoading = document.getElementById('playerLoading');
        const videoPlayer = document.getElementById('videoPlayer');
        
        playerLoading.classList.add('hidden');
        videoPlayer.style.display = 'block';
        
        // Auto-play
        videoPlayer.play().catch(err => {
            console.warn('[BBHC] Auto-play prevented:', err);
        });
    }

    onVideoError(event) {
        console.error('[BBHC] Video playback error:', event);
        
        this.handleStreamError({
            error_code: 'PLAYBACK_ERROR',
            message: 'Failed to play video. Please try again.'
        });
    }

    handleStreamError(error) {
        const playerLoading = document.getElementById('playerLoading');
        
        playerLoading.innerHTML = `
            <i class="fas fa-exclamation-circle" style="font-size: 48px; color: var(--accent-primary);"></i>
            <h3 style="margin: 16px 0 8px 0;">${error.error_code || 'Stream Error'}</h3>
            <p>${error.message || 'Unable to load content'}</p>
            <button onclick="theater.closePlayer()" style="margin-top: 20px; padding: 12px 24px; background: var(--accent-primary); border: none; border-radius: 6px; color: white; cursor: pointer; font-size: 14px; font-weight: 600;">
                Close Player
            </button>
        `;
    }

    closePlayer() {
        const playerModal = document.getElementById('playerModal');
        const videoPlayer = document.getElementById('videoPlayer');
        
        // Pause and reset video
        videoPlayer.pause();
        videoPlayer.currentTime = 0;
        
        // Hide modal
        playerModal.classList.remove('active');
        
        console.log('[BBHC] Player closed');
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize theater when DOM is ready
let theater;
document.addEventListener('DOMContentLoaded', () => {
    theater = new BBHCTheater();
});

// Make theater globally accessible for debugging
window.theater = theater;
