# Timetide

A calm, premium, memory-focused travel diary platform designed for families and individuals documenting trips together.

## Overview

Timetide is a thoughtfully designed web application that feels like a digital archive — timeless, archival, and emotionally warm. It's not a social media app; it's a platform for preserving and sharing travel memories with loved ones.

## Design Philosophy

- **Calm & Minimal**: No bright colors, no infinite scrolling, no gamification
- **Archival**: Feels like a museum catalogue or personal archive
- **Emotional**: Warm, premium design that honors precious memories
- **Collaborative**: Family groups can document trips together
- **Restrained Social Features**: Quiet acknowledgement through likes, no public metrics

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Jinja2 templates with HTML + CSS
- **Database**: PostgreSQL (SQLite for local development)
- **ORM**: SQLAlchemy
- **Authentication**: JWT-based authentication
- **Static Assets**: CSS + images served via /static

## Features

### Core Features
- **Dashboard**: View all trips as beautiful cards with cover photos
- **Trip Pages**: Timeline view of trip with date range calendar
- **Day Timeline**: Vertical timeline showing entries by time with photos
- **Calendar View**: Monthly calendar highlighting days with activity
- **Family Groups**: Collaborate on trips with multiple contributors

### Social Features (Restrained)
- Follow other users
- Like entries (quiet acknowledgement only)
- No like counts displayed
- No notifications by default
- No algorithmic feed

## Project Structure

```
timetide/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── auth/                   # Authentication utilities
│   │   ├── __init__.py
│   │   └── jwt.py             # JWT token handling
│   ├── models/                 # Database models
│   │   ├── __init__.py        # Database connection
│   │   └── database.py        # SQLAlchemy models
│   ├── routes/                 # API routes
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── trips.py           # Trip management
│   │   ├── entries.py         # Entry/journal management
│   │   └── users.py           # User management
│   ├── templates/              # Jinja2 HTML templates
│   │   ├── base.html          # Base template
│   │   ├── navbar.html        # Navigation bar
│   │   ├── dashboard.html     # Dashboard view
│   │   ├── trip.html          # Trip detail view
│   │   ├── day.html           # Day timeline view
│   │   ├── calendar.html      # Calendar view
│   │   ├── profile.html       # User profile
│   │   ├── families.html      # Family groups
│   │   ├── login.html         # Login page
│   │   └── register.html      # Registration page
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Global styles
│   │   └── images/            # Static images
│   └── utils/                  # Utility functions
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL (optional, SQLite works for local dev)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd timetide
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   ```bash
   # Create a .env file
   DATABASE_URL=sqlite:///./timetide.db
   SECRET_KEY=your-secret-key-here
   ```

5. **Initialize the database**
   ```bash
   # Database tables will be created automatically on first run
   ```

6. **Run the application**
   ```bash
   python -m app.main
   # or
   uvicorn app.main:app --reload
   ```

7. **Open your browser**
   Navigate to `http://localhost:8000`

## Database Models

### User
- Authentication and profile information
- Relationships: trips, entries, families, followers

### Trip
- Journey/vacation information
- Fields: title, location, dates, cover_image
- Relationships: owner, entries, families

### Entry
- Individual moments/journal entries
- Fields: content, date, time
- Relationships: trip, author, photos, likes

### Family
- Group collaboration
- Relationships: members (users), trips

### Photo
- Images attached to entries
- Fields: url, caption, order

### Like
- Quiet acknowledgement of entries
- No public counts displayed

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and receive JWT
- `POST /auth/logout` - Logout

### Trips
- `GET /trips/` - Get all user trips
- `GET /trips/{trip_id}` - Get trip details
- `POST /trips/` - Create new trip
- `PUT /trips/{trip_id}` - Update trip
- `DELETE /trips/{trip_id}` - Delete trip

### Entries
- `GET /entries/trip/{trip_id}` - Get trip entries
- `GET /entries/{entry_id}` - Get entry details
- `POST /entries/` - Create new entry
- `PUT /entries/{entry_id}` - Update entry
- `DELETE /entries/{entry_id}` - Delete entry
- `POST /entries/{entry_id}/like` - Like/unlike entry

### Users
- `GET /users/me` - Get current user
- `GET /users/{user_id}` - Get user profile
- `PUT /users/me` - Update profile
- `POST /users/{user_id}/follow` - Follow/unfollow user

## Design System

### Color Palette
- Background: `#FAF9F7` (warm off-white)
- Primary text: `#2E2E2E`
- Secondary text: `#6F6F6F`
- Accent: `#6B8E8A` (muted sage/teal)
- Borders: `#E4E2DD`

### Typography
- Headings: Playfair Display (serif)
- Body: Inter (sans-serif)
- Large margins, generous line height, calm spacing

### UI Principles
- Fixed, minimal navigation bar
- Subtle hover effects (no glow, slight lift only)
- No shadows (minimal use)
- Thin borders in light grey
- No animations beyond subtle transitions

## Deployment

### PostgreSQL Setup (Production)

1. Create a PostgreSQL database
2. Update DATABASE_URL environment variable:
   ```
   DATABASE_URL=postgresql://user:password@localhost/timetide
   ```

### Environment Variables

Required for production:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret (generate a strong random key)

### Deployment Platforms

**Recommended platforms:**
- Railway
- Render
- Heroku
- AWS Elastic Beanstalk
- Google Cloud Run

## Contributing

This is a thoughtfully designed application. When contributing:
- Follow the established design philosophy
- Maintain the calm, archival aesthetic
- No bright colors or busy UI elements
- Keep animations minimal
- Preserve the premium, warm feel

## Future Enhancements

- [ ] Photo upload functionality
- [ ] Trip collaboration invitations
- [ ] Export trip as PDF/book
- [ ] Search across entries
- [ ] Map integration for locations
- [ ] Private/public trip settings
- [ ] Email notifications (opt-in)
- [ ] Mobile responsive improvements
- [ ] PWA support

## License

MIT License

## Contact

For questions or support, please open an issue on GitHub.

---

**Timetide** - Preserving moments, one journey at a time.
