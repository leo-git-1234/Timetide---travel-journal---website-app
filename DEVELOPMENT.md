# Timetide Development Guide

## Getting Started

### Quick Start

**Windows:**
```powershell
.\start.ps1
```

**macOS/Linux:**
```bash
chmod +x start.sh
./start.sh
```

**Manual Start:**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python -m app.main
```

Visit: http://localhost:8000

## Project Structure Explained

```
timetide/
├── app/
│   ├── main.py              # FastAPI app, routes, startup
│   ├── auth/                # JWT authentication
│   ├── models/              # SQLAlchemy database models
│   ├── routes/              # API endpoint definitions
│   ├── templates/           # Jinja2 HTML templates
│   ├── static/              # CSS, images, JS
│   └── utils/               # Helper functions
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variable template
└── README.md               # Project documentation
```

## Key Technologies

### Backend
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation
- **python-jose**: JWT token handling
- **passlib**: Password hashing

### Frontend
- **Jinja2**: Server-side templating
- **Pure CSS**: No frameworks (intentional)
- **Minimal JavaScript**: For interactivity only

## Development Workflow

### 1. Database Changes

The database auto-initializes on first run. For migrations:

```python
# In future: use Alembic for migrations
alembic init alembic
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### 2. Adding New Routes

1. Create route in `app/routes/`
2. Import and include in `app/main.py`
3. Create corresponding template
4. Update CSS if needed

Example:
```python
# app/routes/new_feature.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/endpoint")
async def handler():
    return {"message": "Hello"}

# app/main.py
from app.routes import new_feature
app.include_router(new_feature.router, prefix="/feature", tags=["Feature"])
```

### 3. Creating Templates

All templates extend `base.html`:

```html
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block content %}
<div class="container">
    <!-- Your content -->
</div>
{% endblock %}
```

## Design System Reference

### Colors
```css
--bg-primary: #FAF9F7;     /* Warm off-white */
--text-primary: #2E2E2E;   /* Dark grey */
--text-secondary: #6F6F6F; /* Medium grey */
--accent: #6B8E8A;         /* Sage/teal */
--border: #E4E2DD;         /* Light grey */
```

### Typography
```css
--font-serif: 'Playfair Display';  /* Headings */
--font-sans: 'Inter';               /* Body text */
```

### Spacing
```css
--spacing-xs: 0.5rem;
--spacing-sm: 1rem;
--spacing-md: 1.5rem;
--spacing-lg: 2.5rem;
--spacing-xl: 4rem;
```

## API Development

### Protected Routes

Use the `get_current_user` dependency:

```python
from app.auth import get_current_user
from app.models.database import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user": current_user.username}
```

### Database Queries

```python
from sqlalchemy.orm import Session
from app.models import get_db
from app.models.database import Trip

@router.get("/trips")
async def get_trips(db: Session = Depends(get_db)):
    trips = db.query(Trip).all()
    return trips
```

## Testing

### Manual Testing
1. Start the server
2. Visit http://localhost:8000/docs for API documentation
3. Test endpoints interactively

### Unit Tests (Future)
```bash
pytest
```

## Production Deployment

### Environment Variables
Set these in production:
- `DATABASE_URL` - PostgreSQL connection
- `SECRET_KEY` - Strong random key
- `DEBUG=False`

### Database Migration
1. Update `DATABASE_URL` to PostgreSQL
2. Run application to create tables
3. Use Alembic for schema changes

### Security Checklist
- [ ] Change `SECRET_KEY` to strong random value
- [ ] Use HTTPS in production
- [ ] Set up CORS properly
- [ ] Enable rate limiting
- [ ] Set secure cookie flags
- [ ] Review file upload sizes
- [ ] Enable database backups

## Common Tasks

### Add a New Page
1. Create template in `app/templates/`
2. Add route in `app/main.py`
3. Update navbar if needed

### Modify Styles
Edit `app/static/css/style.css`
- Keep designs calm and minimal
- No bright colors
- Subtle transitions only

### Add Database Model
1. Define in `app/models/database.py`
2. Import in routes
3. Restart app (auto-creates tables)

## Troubleshooting

### Database Issues
```bash
# Delete and recreate database
rm timetide.db
python -m app.main  # Auto-creates
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Template Not Found
- Check path in templates directory
- Ensure `app/templates/` prefix
- Verify template name spelling

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Document functions
- Keep functions small

### HTML/Templates
- Use semantic HTML
- Keep templates simple
- Extend base.html
- Use Jinja2 filters

### CSS
- Follow existing patterns
- Use CSS variables
- Mobile-first responsive
- Minimal animations

## Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- Jinja2 Docs: https://jinja.palletsprojects.com/

## Support

For issues or questions:
1. Check this guide
2. Review existing code patterns
3. Consult framework documentation
4. Open GitHub issue

---

**Remember:** Timetide is about creating a calm, thoughtful experience for preserving memories. Every feature should honor this philosophy.
