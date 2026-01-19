"""Utility functions for Timetide application."""

from datetime import datetime, date, timedelta
from typing import List, Tuple


def get_date_range(start_date: date, end_date: date) -> List[date]:
    """
    Generate a list of dates between start_date and end_date (inclusive).
    
    Args:
        start_date: Starting date
        end_date: Ending date
        
    Returns:
        List of dates from start to end
    """
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]


def format_date_range(start_date: date, end_date: date) -> str:
    """
    Format a date range for display.
    
    Examples:
        - Same month: "June 15-20, 2024"
        - Different months: "June 28 - July 5, 2024"
        - Different years: "Dec 30, 2023 - Jan 5, 2024"
    
    Args:
        start_date: Starting date
        end_date: Ending date
        
    Returns:
        Formatted date range string
    """
    if start_date.year != end_date.year:
        return f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
    elif start_date.month != end_date.month:
        return f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
    else:
        return f"{start_date.strftime('%B %d')}-{end_date.day}, {end_date.year}"


def get_calendar_month_data(year: int, month: int) -> Tuple[List[List[int]], int, int]:
    """
    Get calendar data for a specific month.
    
    Args:
        year: Year
        month: Month (1-12)
        
    Returns:
        Tuple of (calendar_grid, days_in_month, start_weekday)
        - calendar_grid: 2D list representing weeks and days
        - days_in_month: Total days in the month
        - start_weekday: Weekday of first day (0=Monday, 6=Sunday)
    """
    from calendar import monthrange
    
    start_weekday, days_in_month = monthrange(year, month)
    
    # Adjust to start week on Sunday (US convention)
    start_weekday = (start_weekday + 1) % 7
    
    # Build calendar grid
    calendar_grid = []
    current_week = [0] * start_weekday  # Pad beginning
    
    for day in range(1, days_in_month + 1):
        current_week.append(day)
        if len(current_week) == 7:
            calendar_grid.append(current_week)
            current_week = []
    
    # Pad last week if needed
    if current_week:
        current_week.extend([0] * (7 - len(current_week)))
        calendar_grid.append(current_week)
    
    return calendar_grid, days_in_month, start_weekday


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rstrip() + suffix


def get_initials(name: str) -> str:
    """
    Get initials from a name.
    
    Args:
        name: Full name
        
    Returns:
        Initials (up to 2 characters)
    """
    parts = name.strip().split()
    if len(parts) == 0:
        return "?"
    elif len(parts) == 1:
        return parts[0][0].upper()
    else:
        return (parts[0][0] + parts[-1][0]).upper()
