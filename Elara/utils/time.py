import re
from datetime import timedelta

def parse_duration(duration: str) -> timedelta:
    """Parses a duration string like '1d', '2hr', '30m', '10s' into a timedelta."""
    pattern = re.compile(r'(\d+)\s*(d|hr|m|s)')
    matches = pattern.findall(duration.lower())
    
    if not matches:
        return None
        
    total_seconds = 0
    for value, unit in matches:
        value = int(value)
        if unit == 'd':
            total_seconds += value * 86400
        elif unit == 'hr':
            total_seconds += value * 3600
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 's':
            total_seconds += value
            
    return timedelta(seconds=total_seconds)
