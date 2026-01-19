"""
Database models for Timetide travel diary application.
Uses SQLAlchemy ORM with support for PostgreSQL and SQLite.
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, Table, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Association tables for many-to-many relationships

# Users can follow other users
followers = Table(
    'followers',
    Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('followed_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

# Users can be members of multiple families
family_members = Table(
    'family_members',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('family_id', Integer, ForeignKey('families.id'), primary_key=True),
    Column('joined_at', DateTime, default=datetime.utcnow),
    Column('role', String(50), default='member')  # 'admin' or 'member'
)

# Families can have multiple trips
family_trips = Table(
    'family_trips',
    Base.metadata,
    Column('family_id', Integer, ForeignKey('families.id'), primary_key=True),
    Column('trip_id', Integer, ForeignKey('trips.id'), primary_key=True)
)


class User(Base):
    """User model for authentication and profile management."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trips = relationship('Trip', back_populates='owner', cascade='all, delete-orphan')
    entries = relationship('Entry', back_populates='author', cascade='all, delete-orphan')
    families = relationship('Family', secondary=family_members, back_populates='members')
    likes = relationship('Like', back_populates='user', cascade='all, delete-orphan')
    
    # Following relationships
    following = relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref='followers'
    )
    
    def __repr__(self):
        return f"<User {self.username}>"


class Family(Base):
    """Family/Group model for collaborative trip documentation."""
    __tablename__ = 'families'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = relationship('User', secondary=family_members, back_populates='families')
    trips = relationship('Trip', secondary=family_trips, back_populates='families')
    
    def __repr__(self):
        return f"<Family {self.name}>"


class Trip(Base):
    """Trip model representing a journey/vacation."""
    __tablename__ = 'trips'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    cover_image = Column(String(500), nullable=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    owner = relationship('User', back_populates='trips')
    entries = relationship('Entry', back_populates='trip', cascade='all, delete-orphan')
    families = relationship('Family', secondary=family_trips, back_populates='trips')
    media = relationship('TripMedia', back_populates='trip', cascade='all, delete-orphan')
    
    @property
    def num_days(self):
        """Calculate the number of days in the trip."""
        return (self.end_date - self.start_date).days + 1
    
    @property
    def num_entries(self):
        """Get the number of entries in this trip."""
        return len(self.entries)
    
    @property
    def num_photos(self):
        """Get the total number of photos across all entries."""
        return sum(len(entry.photos) for entry in self.entries)
    
    @property
    def num_locations(self):
        """Get the number of unique locations in this trip."""
        unique_locations = set()
        for entry in self.entries:
            if entry.location and entry.location.place_name:
                unique_locations.add(entry.location.place_name)
        return len(unique_locations)
    
    @property
    def contributors(self):
        """Get list of unique contributors (family members who authored entries)."""
        contributor_ids = set(entry.author_id for entry in self.entries)
        return [entry.author for entry in self.entries if entry.author_id in contributor_ids]
    
    def __repr__(self):
        return f"<Trip {self.title}>"


class Location(Base):
    """Location model for geographic data of entries."""
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True, index=True)
    place_name = Column(String(255), nullable=True)  # e.g., "Eiffel Tower, Paris"
    latitude = Column(String(50), nullable=True)  # Stored as string for precision
    longitude = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    entries = relationship('Entry', back_populates='location')
    
    def __repr__(self):
        return f"<Location {self.place_name}>"


class Entry(Base):
    """Entry model for individual moments/journal entries within a trip."""
    __tablename__ = 'entries'
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    entry_date = Column(Date, nullable=False)
    entry_time = Column(String(10), nullable=True)  # e.g., "14:30"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    
    # Relationships
    trip = relationship('Trip', back_populates='entries')
    author = relationship('User', back_populates='entries')
    location = relationship('Location', back_populates='entries')
    photos = relationship('Photo', back_populates='entry', cascade='all, delete-orphan')
    likes = relationship('Like', back_populates='entry', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Entry {self.id} by {self.author.username}>"


class Photo(Base):
    """Photo model for images attached to entries."""
    __tablename__ = 'photos'
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False)
    caption = Column(Text, nullable=True)
    order = Column(Integer, default=0)  # For ordering multiple photos in an entry
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    entry_id = Column(Integer, ForeignKey('entries.id'), nullable=False)
    
    # Relationships
    entry = relationship('Entry', back_populates='photos')
    
    def __repr__(self):
        return f"<Photo {self.id}>"


class TripMedia(Base):
    """TripMedia model for images and videos attached to trips."""
    __tablename__ = 'trip_media'
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False)  # Base64 or file path
    media_type = Column(String(20), nullable=False)  # 'image' or 'video'
    file_name = Column(String(255), nullable=True)
    order = Column(Integer, default=0)  # For ordering multiple media in a trip
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    
    # Relationships
    trip = relationship('Trip', back_populates='media')
    
    def __repr__(self):
        return f"<TripMedia {self.id} ({self.media_type})>"


class Like(Base):
    """Like model for quiet acknowledgement of entries."""
    __tablename__ = 'likes'
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    entry_id = Column(Integer, ForeignKey('entries.id'), nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='likes')
    entry = relationship('Entry', back_populates='likes')
    
    def __repr__(self):
        return f"<Like by {self.user.username} on Entry {self.entry_id}>"
