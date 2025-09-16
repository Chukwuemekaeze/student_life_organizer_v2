from datetime import datetime
import os
from functools import wraps

def get_current_year():
    """Get the current year, which can be overridden by environment variable."""
    return int(os.getenv('CURRENT_YEAR', datetime.now().year))

def with_custom_year(f):
    """Decorator to modify datetime.now() to use the custom year."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        current_year = get_current_year()
        now = datetime.now()
        if now.year != current_year:
            # Create a new datetime with the custom year
            now = now.replace(year=current_year)
        return f(*args, **kwargs)
    return wrapper
