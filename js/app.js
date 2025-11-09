// BBHC Theatre - Main Application Script
// Handles UI interactions, content filtering, search, and video playback

class BBHCTheatre {
    constructor() {
        this.allContent = [];
        this.filteredContent = [];
        this.currentCategory = 'all';
        this.searchQuery = '';
        this.currentContentItem = null;
        this.selectedQualityIndex = 0;
        this.searchTimeout = null;
        
        // Backend API configuration
        this.API_BASE_URL = 'http://localhost:5000';
        this.USE_BACKEND = true; // Set to false to use mock data
        this.USE_BACKEND_ON_STARTUP = false; // Load local data first
        
        this.init();
    }

    async init() {
        console.log('[BBHC] Initializing theatre...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Show skeleton loaders initially
        this.showSkeletonLoaders();
        
        // Load initial content from local data.js
        this.allContent = window.contentDatabase || [];
        this.filteredContent = [...this.allContent];
        
        if (this.allContent.length > 0) {
            console.log(`[BBHC] Loaded ${this.allContent.length} movies from local database`);
            await this.delay(500);
            this.renderContent();
            this.updateCategoryTitle('Featured Movies');
        } else {
            console.log('[BBHC] No local content found');
            this.showError('No content available. Use search to find movies.');
        }
        
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
            this.searchQuery = e.target.value.toLowerCase().trim();
            
            // Clear previous timeout
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }
            
            // Wait 500ms after user stops typing before searching
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
        
        if (this.USE_BACKEND && this.searchQuery) {
            // Search via backend API
            await this.performBackendSearch(this.searchQuery);
        } else {
            // Filter local content
            this.filteredContent = this.allContent.filter(item => {
                const matchesSearch = !this.searchQuery || 
                    item.title.toLowerCase().includes(this.searchQuery) ||
                    (item.description && item.description.toLowerCase().includes(this.searchQuery));
                
                let matchesCategory = true;
                if (this.currentCategory !== 'all') {
                    if (this.currentCategory === 'movies') {
                        matchesCategory = !item.is_series;
                    } else if (this.currentCategory === 'series') {
                        matchesCategory = item.is_series;
                    } else if (this.currentCategory.startsWith('genre-')) {
                        const genre = this.currentCategory.replace('genre-', '');
                        matchesCategory = item.genre && item.genre.some(g => 
                            g.toLowerCase() === genre.toLowerCase()
                        );
                    } else if (this.currentCategory.startsWith('year-')) {
                        const year = parseInt(this.currentCategory.replace('year-', ''));
                        matchesCategory = item.year === year;
                    } else if (this.currentCategory.startsWith('language-')) {
                        const language = this.currentCategory.replace('language-', '').toLowerCase();
                        const itemLanguage = (item.language || 'english').toLowerCase();
                        matchesCategory = itemLanguage === language;
                    }
                }
                
                return matchesSearch && matchesCategory;
            });
            
            this.updateCategoryTitle(`Search: "${this.searchQuery}"`);
            setTimeout(() => this.renderContent(), 400);
        }
    }

    async performBackendSearch(query) {
        try {
            this.showSkeletonLoaders();
            this.updateCategoryTitle(`Searching for "${query}"...`);
            
            const startTime = Date.now();
            const response = await fetch(`${this.API_BASE_URL}/api/search?q=${encodeURIComponent(query)}`);
            
            if (!response.ok) {
                throw new Error(`Search failed: ${response.statusText}`);
            }
            
            const data = await response.json();
            const searchTime = ((Date.now() - startTime) / 1000).toFixed(2);
            
            // Transform backend results to match frontend format
            this.allContent = data.results.map(item => ({
                id: item.id,
                title: item.title,
                poster_url: item.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster',
                year: item.year || 2024,
                genre: item.genre || ['Unknown'],
                imdb_rating: item.imdb_rating || 'N/A',
                description: item.snippet || 'No description available',
                is_series: false,
                qualities: item.qualities || [],
                message_chat_id: item.message_chat_id,
                message_id: item.message_id,
                cast: ['Cast information not available'],
                imdb_id: 'tt0000000'
            }));
            
            this.filteredContent = [...this.allContent];
            this.updateCategoryTitle(`Found ${data.total} results for "${query}" (${searchTime}s)`);
            this.renderContent();
            
            console.log(`[BBHC] Found ${data.total} results from backend in ${searchTime}s`);
        } catch (error) {
            console.error('[BBHC] Backend search failed:', error);
            this.updateCategoryTitle(`Search failed for "${query}"`);
            this.showError('Search failed. Please try again.');
        }
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
        const genres = (item.genre || []).slice(0, 2).map(g => 
            `<span class="genre-tag">${g}</span>`
        ).join('');
        
        const type = item.is_series ? 'Series' : 'Movie';
        const rating = item.imdb_rating || 'N/A';
        
        // Show quality badges if available
        const qualityBadges = (item.qualities || []).slice(0, 3).map(q => 
            `<span class="quality-badge">${q.label}</span>`
        ).join('');
        
        return `
            <div class="content-card" data-id="${item.id}">
                <div class="card-poster">
                    <img src="${item.poster_url}" alt="${item.title}" onerror="this.src='https://via.placeholder.com/300x450/1a1a1a/e50914?text=${encodeURIComponent(item.title)}'">
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
                    ${qualityBadges ? `<div class="card-qualities">${qualityBadges}</div>` : ''}
                </div>
            </div>
        `;
    }

    showDetailModal(contentId) {
        const item = this.allContent.find(c => c.id === contentId);
        if (!item) return;
        
        this.currentContentItem = item;
        
        // Populate modal
        const modalPoster = document.getElementById('modalPoster');
        modalPoster.src = item.poster_url;
        modalPoster.onerror = function() {
            this.src = 'https://via.placeholder.com/300x450/1a1a1a/e50914?text=' + encodeURIComponent(item.title);
        };
        document.getElementById('modalTitle').textContent = item.title;
        document.getElementById('modalRating').textContent = item.imdb_rating || 'N/A';
        document.getElementById('modalYear').textContent = item.year;
        document.getElementById('modalType').textContent = item.is_series ? 'Series' : 'Movie';
        document.getElementById('modalDescription').textContent = item.description || item.snippet || 'No description available';
        document.getElementById('modalCast').textContent = (item.cast || []).join(', ') || 'Cast information not available';
        
        // Render genres
        const genresHTML = (item.genre || []).map(g => 
            `<span class="modal-genre-tag">${g}</span>`
        ).join('');
        document.getElementById('modalGenres').innerHTML = genresHTML || '<span class="modal-genre-tag">Unknown</span>';
        
        // Set IMDB link
        const imdbLink = document.getElementById('modalImdbLink');
        imdbLink.href = `https://www.imdb.com/title/${item.imdb_id || 'tt0000000'}/`;

        // Render quality options if available
        if (item.qualities && item.qualities.length > 0) {
            const qualitiesHTML = item.qualities.map((q, index) => 
                `<button class="quality-btn ${index === 0 ? 'active' : ''}" data-index="${index}">${q.label}</button>`
            ).join('');
            
            const qualityContainer = document.getElementById('modalQualities');
            if (qualityContainer) {
                qualityContainer.innerHTML = qualitiesHTML;
                
                // Add click handlers for quality buttons
                qualityContainer.querySelectorAll('.quality-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        qualityContainer.querySelectorAll('.quality-btn').forEach(b => b.classList.remove('active'));
                        e.target.classList.add('active');
                        this.selectedQualityIndex = parseInt(e.target.dataset.index);
                    });
                });
            }
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
        playerTitle.title = this.currentContentItem.title;
        playerModal.classList.add('active');
        playerLoading.classList.remove('hidden');
        videoPlayer.style.display = 'none';
        
        try {
            if (this.USE_BACKEND) {
                // Request stream from backend
                const streamUrl = await this.requestStreamFromBackend(
                    this.currentContentItem.id,
                    this.selectedQualityIndex
                );
                
                // Load video
                videoSource.src = streamUrl;
                videoPlayer.load();
                
                console.log('[BBHC] ✓ Stream loaded successfully');
            } else {
                // Use mock streaming URL
                const streamingUrl = await window.telegramLoader.resolveStreamingUrl(
                    this.currentContentItem.id,
                    this.currentContentItem
                );
                
                videoSource.src = streamingUrl;
                videoPlayer.load();
            }
            
        } catch (error) {
            console.error('[BBHC] Stream loading failed:', error);
            this.handleStreamError(error);
        }
    }
    
    async requestStreamFromBackend(itemId, qualityIndex) {
        try {
            // Update loading message
            const playerLoading = document.getElementById('playerLoading');
            playerLoading.innerHTML = `
                <div class="spinner"></div>
                <p>Requesting stream...</p>
            `;
            
            // Request stream
            const response = await fetch(`${this.API_BASE_URL}/api/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    item_id: itemId,
                    quality_index: qualityIndex
                })
            });
            
            if (!response.ok) {
                throw new Error(`Stream request failed: ${response.statusText}`);
            }
            
            const data = await response.json();
            const jobId = data.job_id;
            
            console.log(`[BBHC] Stream job created: ${jobId}`);
            
            // Poll for job completion
            return await this.pollStreamJob(jobId);
            
        } catch (error) {
            console.error('[BBHC] Stream request failed:', error);
            throw error;
        }
    }
    
    async pollStreamJob(jobId) {
        const maxAttempts = 60; // 60 seconds max
        let attempts = 0;
        
        while (attempts < maxAttempts) {
            try {
                const response = await fetch(`${this.API_BASE_URL}/api/job/${jobId}`);
                
                if (!response.ok) {
                    throw new Error(`Job status check failed: ${response.statusText}`);
                }
                
                const job = await response.json();
                
                // Update loading message with progress
                const playerLoading = document.getElementById('playerLoading');
                playerLoading.innerHTML = `
                    <div class="spinner"></div>
                    <p>${job.progress || 'Processing...'}</p>
                `;
                
                if (job.status === 'done' && job.stream_url) {
                    console.log('[BBHC] Stream ready:', job.stream_url);
                    return job.stream_url;
                }
                
                if (job.status === 'failed') {
                    throw new Error(job.error || 'Stream job failed');
                }
                
                // Wait 1 second before next poll
                await this.delay(1000);
                attempts++;
                
            } catch (error) {
                console.error('[BBHC] Job polling error:', error);
                throw error;
            }
        }
        
        throw new Error('Stream request timed out');
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
        
        // Check if it's a streaming bot configuration error
        const errorMsg = error.message || error.toString() || 'Unable to load content';
        const isConfigError = errorMsg.includes('Streaming bot not configured') || errorMsg.includes('STREAMING_BOT_USERNAME');
        
        let helpText = '';
        if (isConfigError) {
            helpText = `
                <div style="margin-top: 20px; padding: 15px; background: rgba(229, 9, 20, 0.1); border-radius: 8px; text-align: left; max-width: 500px; margin-left: auto; margin-right: auto;">
                    <h4 style="margin: 0 0 10px 0; color: var(--accent-primary);">⚙️ Setup Required</h4>
                    <p style="margin: 0 0 10px 0; font-size: 14px;">To enable streaming, you need to configure a streaming bot:</p>
                    <ol style="margin: 0; padding-left: 20px; font-size: 13px; line-height: 1.6;">
                        <li>Search for <strong>@TG_FileStreamBot</strong> on Telegram</li>
                        <li>Start the bot and test it with any video file</li>
                        <li>Create a <code>.env</code> file with: <code>STREAMING_BOT_USERNAME=TG_FileStreamBot</code></li>
                        <li>Restart the backend server</li>
                    </ol>
                    <p style="margin: 10px 0 0 0; font-size: 12px; color: var(--text-secondary);">
                        See <strong>STREAMING_SETUP.md</strong> for detailed instructions.
                    </p>
                </div>
            `;
        }
        
        playerLoading.innerHTML = `
            <i class="fas fa-exclamation-circle" style="font-size: 48px; color: var(--accent-primary);"></i>
            <h3 style="margin: 16px 0 8px 0;">${error.error_code || 'Stream Error'}</h3>
            <p style="max-width: 600px; margin: 0 auto 10px;">${errorMsg}</p>
            ${helpText}
            <button onclick="theater.closePlayer()" style="margin-top: 20px; padding: 12px 24px; background: var(--accent-primary); border: none; border-radius: 6px; color: white; cursor: pointer; font-size: 14px; font-weight: 600;">
                Close Player
            </button>
        `;
    }
    
    showError(message) {
        const contentGrid = document.getElementById('contentGrid');
        contentGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
                <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: var(--accent-primary); margin-bottom: 20px;"></i>
                <h3 style="color: var(--text-primary); margin-bottom: 10px;">Error</h3>
                <p style="color: var(--text-secondary);">${message}</p>
            </div>
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
