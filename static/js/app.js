// BBHC Theatre - Main Application Script
// Handles UI interactions, content filtering, search, and video playback

class BBHCTheatre {
    constructor() {
        this.allContent = [];
        this.filteredContent = [];
        this.currentCategory = 'all';
        this.searchQuery = '';
        this.currentContentItem = null;
        this.searchTimeout = null;
        
        this.init();
    }

    async init() {
    console.log('[BBHC] Initializing theatre...');
        
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
        
    console.log('[BBHC] ✓ Theatre ready');
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

        // Search functionality with debounce
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');

        searchInput.addEventListener('input', (e) => {
            this.searchQuery = e.target.value.trim();
            
            // Clear previous timeout
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }
            
            // Wait 500ms after user stops typing before searching (reduced from 2s)
            this.searchTimeout = setTimeout(() => {
                console.log('[BBHC] Search triggered after delay');
                this.performSearch();
            }, 500);
        });

        searchBtn.addEventListener('click', () => {
            // Immediate search on button click
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }
            this.performSearch();
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                // Immediate search on Enter key
                if (this.searchTimeout) {
                    clearTimeout(this.searchTimeout);
                }
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
            document.body.classList.add('no-scroll');
        } else {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
            document.body.classList.remove('no-scroll');
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
        } else if (filter.startsWith('language-')) {
            const language = filter.replace('language-', '').toLowerCase();
            this.filteredContent = this.allContent.filter(item => {
                const itemLanguage = (item.language || 'english').toLowerCase();
                return itemLanguage === language;
            });
            const title = language.charAt(0).toUpperCase() + language.slice(1);
            this.updateCategoryTitle(title);
        }
        
        // Apply search if active
        if (this.searchQuery) {
            this.performSearch();
        } else {
            // Simulate loading delay
            setTimeout(() => this.renderContent(), 500);
        }
    }

    async performSearch() {
        console.log(`[BBHC] Searching: ${this.searchQuery}`);
        
        if (!this.searchQuery) {
            this.filteredContent = [...this.allContent];
            this.updateCategoryTitle('All Content');
            this.renderContent();
            return;
        }
        
        // Show skeleton loaders
        this.showSkeletonLoaders();
        this.updateCategoryTitle(`Searching for "${this.searchQuery}"...`);
        
        try {
            // Call Flask API to search movies
            const response = await fetch('/api/search-movie', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: this.searchQuery})
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Convert API results to content format
                this.filteredContent = data.results.map((result, index) => ({
                    id: `search-${index}`,
                    title: result.title,
                    description: `Click to stream this movie`,
                    thumbnail: 'https://placehold.co/300x450/141414/e50914?text=' + encodeURIComponent(result.title),
                    year: new Date().getFullYear(),
                    rating: '⭐',
                    genre: ['Movie'],
                    language: 'Multi',
                    is_series: false,
                    message_id: result.message_id,
                    row: result.row,
                    col: result.col
                }));
                
                console.log(`[BBHC] Found ${this.filteredContent.length} results`);
                this.updateCategoryTitle(`Found ${this.filteredContent.length} results for "${this.searchQuery}"`);
            } else {
                console.error('[BBHC] Search failed:', data.error);
                this.filteredContent = [];
                this.updateCategoryTitle(`No results for "${this.searchQuery}"`);
            }
        } catch (error) {
            console.error('[BBHC] Search error:', error);
            this.filteredContent = [];
            this.updateCategoryTitle(`Search failed for "${this.searchQuery}"`);
        }
        
        // Render results immediately (removed artificial delay)
        this.renderContent();
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
        
        const posterUrl = item.poster_url || item.thumbnail || 'https://placehold.co/300x450/141414/e50914?text=' + encodeURIComponent(item.title);
        const rating = item.imdb_rating || item.rating || 'N/A';
        
        return `
            <div class="content-card" data-id="${item.id}">
                <div class="card-poster">
                    <img src="${posterUrl}" alt="${item.title}" onerror="this.src='https://placehold.co/300x450/141414/e50914?text=No+Image'">
                    <div class="card-rating">
                        <i class="fas fa-star"></i>
                        <span>${rating}</span>
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
        // Prefer the currently rendered items (search results) first
        let item = (this.filteredContent || []).find(c => c.id === contentId);
        if (!item) {
            item = (this.allContent || []).find(c => c.id === contentId);
        }
        if (!item) return;
        
        this.currentContentItem = item;
        
        // Populate modal
        const fallbackPoster = 'https://placehold.co/300x450/141414/e50914?text=' + encodeURIComponent(item.title || 'No Image');
        document.getElementById('modalPoster').src = item.poster_url || item.thumbnail || fallbackPoster;
        document.getElementById('modalTitle').textContent = item.title || 'Unknown Title';
        document.getElementById('modalRating').textContent = (item.imdb_rating != null ? item.imdb_rating : (item.rating != null ? item.rating : 'N/A'));
        document.getElementById('modalYear').textContent = item.year != null ? item.year : '';
        document.getElementById('modalType').textContent = item.is_series ? 'Series' : 'Movie';
        document.getElementById('modalDescription').textContent = item.description || 'No description available.';
        const castArray = Array.isArray(item.cast) ? item.cast : [];
        document.getElementById('modalCast').textContent = castArray.join(', ');
        
        // Render genres
        const genresHTML = item.genre.map(g => 
            `<span class="modal-genre-tag">${g}</span>`
        ).join('');
        document.getElementById('modalGenres').innerHTML = genresHTML;
        
        // Set IMDB link
        const imdbLink = document.getElementById('modalImdbLink');
        imdbLink.href = item && item.imdb_id ? `https://www.imdb.com/title/${item.imdb_id}/` : 'https://www.imdb.com/';

        // Set Download link
        const downloadLink = document.getElementById('modalDownloadLink');
        if (item.message_id !== undefined && item.row !== undefined && item.col !== undefined) {
            const params = new URLSearchParams({
                message_id: String(item.message_id),
                row: String(item.row),
                col: String(item.col)
            });
            downloadLink.href = `/api/download?${params.toString()}`;
            downloadLink.removeAttribute('download');
        } else if (item.streaming_url) {
            downloadLink.href = item.streaming_url;
            downloadLink.setAttribute('download', `${item.title.replace(/\s+/g, '_')}.mp4`);
        } else {
            downloadLink.href = '#';
        }
        
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
            // Check if this is a search result with message_id
            if (this.currentContentItem.message_id) {
                console.log('[BBHC] Getting stream link from backend...');
                
                // Call Flask API to get stream link
                const response = await fetch('/api/get-stream-link', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message_id: this.currentContentItem.message_id,
                        row: this.currentContentItem.row,
                        col: this.currentContentItem.col
                    })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    // Load video from stream URL
                    videoSource.src = data.stream_url;
                    videoPlayer.load();
                    console.log('[BBHC] ✓ Stream loaded successfully');
                } else {
                    throw new Error(data.error || 'Failed to get stream link');
                }
            } else {
                // Fallback for demo content
                if (this.currentContentItem.video_url) {
                    videoSource.src = this.currentContentItem.video_url;
                    videoPlayer.load();
                } else {
                    throw new Error('No video URL available. Please search for movies to stream.');
                }
            }
            
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

// Initialize theatre when DOM is ready
let theater;
document.addEventListener('DOMContentLoaded', () => {
    theater = new BBHCTheatre();
});

// Make theater globally accessible for debugging
window.theater = theater;
