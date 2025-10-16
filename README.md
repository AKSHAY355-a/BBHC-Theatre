# 🎬 BBHC Theater - Streaming Website

A modern, responsive streaming platform for movies and series with dark-themed UI and Telegram-based content delivery.

## 🌟 Features

### ✅ Currently Completed Features

1. **Modern Dark-Themed UI**
   - Fully responsive design for mobile, tablet, and desktop
   - Netflix-inspired interface with smooth animations
   - Gradient accents and hover effects
   - Custom scrollbar styling

2. **Content Browsing System**
   - Horizontal card layout with poster images
   - Display of IMDB ratings, year, and genres
   - Skeleton loading animations for smooth UX
   - 20+ sample movies and series with real data

3. **Advanced Navigation**
   - Hamburger sidebar menu with categories
   - Filter by: All Content, Movies, Series
   - Genre filtering: Action, Thriller, Comedy, Drama, Horror, Sci-Fi
   - Year filtering: 2024, 2023, 2022, 2021
   - Smooth sidebar animations with overlay

4. **Real-Time Search**
   - Search by title or description
   - Live filtering as you type
   - Combined search with category filters
   - "No results" state with helpful message

5. **Content Detail Modal**
   - Full movie/series information display
   - IMDB data integration with direct links
   - Cast information
   - Genre tags and metadata
   - Synopsis/description
   - "Start Streaming" call-to-action button

6. **Integrated Video Player**
   - Full-screen capable player
   - Standard HTML5 controls (play, pause, seek, volume, fullscreen)
   - Loading animations with spinner
   - Error handling with user-friendly messages
   - Automatic play-on-load

7. **Telegram Backend Integration**
   - Chunked loading support for fast playback
   - Content URL resolution via Telegram
   - Cache management system
   - WebRTC structure for peer-to-peer streaming
   - Format handling (.mov and other formats)
   - Progress tracking during downloads

8. **Performance Optimizations**
   - Skeleton loading states
   - Lazy content rendering
   - Efficient filtering and search
   - Memory management for video playback

## 📁 Project Structure

```
BBHC-Theater/
├── index.html              # Main HTML structure
├── css/
│   └── style.css          # Dark theme styles & animations
├── js/
│   ├── app.js             # Main application logic
│   ├── data.js            # Sample movie/series database
│   └── telegram.js        # Telegram integration module
└── README.md              # Project documentation
```

## 🎯 Functional Entry Points

### Main Page
- **URL**: `index.html`
- **Description**: Home page with all content displayed
- **Features**: Hero section, content grid, search, navigation

### Navigation Filters
- **All Content**: Shows all movies and series
- **Movies**: Filter to show only movies (`is_series: false`)
- **Series**: Filter to show only TV series (`is_series: true`)
- **Genre Filters**: Action, Thriller, Comedy, Drama, Horror, Sci-Fi
- **Year Filters**: 2024, 2023, 2022, 2021

### Search Functionality
- **Location**: Header search bar
- **Behavior**: Real-time filtering, searches title and description
- **Combined Filters**: Works together with category filters

### Content Actions
- **Click Card**: Opens detail modal with full information
- **Start Streaming**: Loads video player with content
- **IMDB Link**: Opens IMDB page in new tab

## 🗄️ Data Models & Schema

### Movie/Series Card Object
```json
{
  "id": "string",           // Unique identifier
  "title": "string",
  "poster_url": "string",   // URL to thumbnail/poster
  "year": "integer",
  "genre": ["string"],      // Array of genres
  "imdb_rating": "number",  // e.g. 7.5
  "description": "string",
  "is_series": "boolean"    // true for series, false for movies
}
```

### Detailed Movie/Series View
```json
{
  "id": "string",
  "title": "string",
  "poster_url": "string",
  "year": "integer",
  "genre": ["string"],
  "imdb_id": "string",      // IMDB identifier
  "imdb_rating": "number",
  "cast": ["string"],       // Array of cast members
  "description": "string",
  "streaming_url": "string", // Resolved streaming URL
  "player_controls": ["Play", "Pause", "Seek", "Fullscreen", "Volume"]
}
```

### Search Result Response
```json
{
  "query": "string",
  "results": [/* Array of Movie/Series Card Objects */],
  "total": "integer"
}
```

### Error Response
```json
{
  "error_code": "string",   // e.g. "CONTENT_NOT_FOUND", "STREAM_FAILED"
  "message": "string"
}
```

## 🔧 Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Icons**: Font Awesome 6.4.0
- **Fonts**: Google Fonts (Inter)
- **Video**: HTML5 Video with custom controls
- **Backend**: Telegram-based content delivery (demo mode)

## 🚀 Usage Instructions

### For Development
1. Open `index.html` in a modern web browser
2. Browse content using the navigation menu
3. Search for movies/series using the search bar
4. Click any content card to view details
5. Click "Start Streaming" to watch content

### Browser Compatibility
- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 📊 Sample Content

The website includes 20 high-quality sample movies and series:

**Movies**: Inception, The Dark Knight, Interstellar, Parasite, The Shawshank Redemption, Pulp Fiction, Get Out, The Grand Budapest Hotel, Mad Max: Fury Road, Dune, Oppenheimer, Everything Everywhere All at Once, John Wick, The Matrix, The Conjuring, Spider-Man: Across the Spider-Verse, A Quiet Place, Top Gun: Maverick, Barbie, The Batman

**Series**: Breaking Bad, Stranger Things, The Last of Us, The Crown, Wednesday, The Witcher, House of the Dragon, Black Mirror

## 🔐 Backend Integration

### Telegram Content Delivery

The project includes a complete Telegram integration structure for content delivery:

**Current Implementation (Demo Mode)**:
- Mock Telegram connection with logging
- URL resolution simulation
- Chunked loading framework
- Cache management system
- Error handling and fallback mechanisms

**Production Implementation Requirements**:

1. **Telegram Bot API Setup**
   - Create bot via @BotFather
   - Store content in Telegram channels/groups
   - Implement `getFile` API for download URLs
   - Handle large files (>20MB) with proper chunking

2. **Chunked Loading**
   - Implement Range requests for partial content
   - Support adaptive bitrate streaming
   - Enable seek operations in video player
   - Cache chunks in IndexedDB for offline playback

3. **WebRTC Streaming**
   - Set up STUN/TURN servers for NAT traversal
   - Implement signaling server for peer discovery
   - Use MediaSource Extensions for buffer management
   - Handle peer connections and reconnection logic

4. **Format Support**
   - Server-side transcoding with FFmpeg
   - HLS support for iOS devices
   - DASH for adaptive streaming
   - Subtitle tracks and multiple audio streams

5. **Security & Compliance**
   - Validate all content sources
   - Implement rate limiting
   - Use HTTPS for all connections
   - Respect copyright and fair use policies
   - **IMPORTANT**: This project is for personal and fair use only

## ⚠️ Important Notes

### Usage Policy
- This website is designed for **personal and fair use only**
- Content should not be distributed publicly
- Respect copyright laws and regulations
- Implement proper authentication for production use

### Content Sources
- Sample content uses publicly available poster images from TMDB
- Video samples use public domain content from Google
- Production implementation requires proper content licensing

## 🎨 Design Features

### Color Scheme
- Primary Background: `#0a0a0a`
- Secondary Background: `#141414`
- Accent Color: `#e50914` (Netflix Red)
- Text Primary: `#ffffff`
- Text Secondary: `#b3b3b3`

### Animations
- Skeleton loading with shimmer effect
- Card hover with scale and shadow
- Modal slide-in animations
- Smooth sidebar transitions
- Loading spinners

### Responsive Breakpoints
- Desktop: 1024px+
- Tablet: 768px - 1023px
- Mobile: < 768px
- Small Mobile: < 480px

## 🛠️ Features Not Yet Implemented

1. **User Authentication**
   - Login/signup system
   - User profiles and watchlists
   - Viewing history

2. **Advanced Video Features**
   - Subtitle support (SRT/VTT)
   - Multiple audio tracks
   - Quality selection (720p, 1080p, 4K)
   - Picture-in-picture mode

3. **Social Features**
   - User ratings and reviews
   - Comments section
   - Share functionality
   - Recommendations based on viewing history

4. **Content Management**
   - Admin panel for content upload
   - Automated metadata fetching
   - Batch content processing
   - Content categorization tools

5. **Enhanced Backend**
   - Real Telegram Bot API integration
   - Production-ready streaming infrastructure
   - CDN integration
   - Analytics and monitoring

## 📈 Recommended Next Steps

1. **Backend Implementation**
   - Set up Telegram Bot and channels
   - Implement real content delivery system
   - Configure streaming servers
   - Set up CDN for better performance

2. **User Management**
   - Implement authentication system
   - Add user profiles and preferences
   - Create watchlist functionality
   - Track viewing history

3. **Enhanced Features**
   - Add subtitle support
   - Implement multi-quality streaming
   - Add content recommendations
   - Create mobile apps (PWA)

4. **Production Readiness**
   - Set up proper hosting infrastructure
   - Implement SSL/TLS certificates
   - Configure load balancing
   - Set up monitoring and logging
   - Implement backup systems

5. **Legal & Compliance**
   - Obtain content licenses
   - Implement proper DRM if required
   - Add terms of service and privacy policy
   - Ensure GDPR/CCPA compliance

## 🐛 Known Issues

- Video player may not auto-play on some mobile browsers (browser security policy)
- Large video files may take time to load without proper chunking implementation
- Some older browsers may not support all CSS features

## 📝 License

This project is provided for educational and personal use only. All content rights belong to their respective owners.

## 🤝 Contributing

For personal use project. If deploying publicly, ensure all content is properly licensed and compliance requirements are met.

---

**Built with ❤️ for streaming enthusiasts**

For questions or support, refer to the inline code documentation in:
- `js/app.js` - Main application logic
- `js/telegram.js` - Backend integration details
- `js/data.js` - Data structure examples
